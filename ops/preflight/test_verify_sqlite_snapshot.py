"""Synthetic-only SQLite fixtures; no real Hermes database access."""
import contextlib
from io import StringIO
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

from unittest.mock import patch
import verify_sqlite_snapshot as snapshot_module
from verify_sqlite_snapshot import BackupError, MAX_BYTES, main, validate_snapshot


class OfflineSnapshotTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.file = self.root / "TOP_SECRET_BACKUP.db"
        with contextlib.closing(sqlite3.connect(self.file)) as db:
            with db:
                db.execute("CREATE TABLE sample(id INTEGER PRIMARY KEY, secret TEXT)")
                db.execute("INSERT INTO sample(secret) VALUES(?)", ("PRIVATE_FIXTURE_VALUE",))

    def test_roundtrip_is_memory_only(self):
        original = self.file.read_bytes()
        report = validate_snapshot(self.file)
        self.assertEqual("PASS", report["sqlite_integrity"])
        self.assertEqual(1, report["restored_table_count"])
        self.assertEqual("NOT_TESTED", report["hermes_functional_restore"])
        self.assertEqual("UNVERIFIED", report["owner_windows_p0"])
        self.assertFalse(report["production_ready"])
        self.assertEqual(original, self.file.read_bytes())
        self.assertEqual([self.file.name], [f.name for f in self.root.iterdir()])

    def test_no_path_secret_or_table_data_escapes(self):
        buf = StringIO()
        with contextlib.redirect_stdout(buf):
            exit_code = main(["--snapshot", str(self.file)])
        self.assertEqual(0, exit_code)
        for private in ("TOP_SECRET_BACKUP", "PRIVATE_FIXTURE_VALUE", str(self.root)):
            self.assertNotIn(private, buf.getvalue())
        self.assertEqual("PASS", json.loads(buf.getvalue())["sqlite_integrity"])


    def test_independent_digest_match_is_explicit(self):
        import hashlib
        digest = hashlib.sha256(self.file.read_bytes()).hexdigest()
        result = validate_snapshot(self.file, expected_sha256=digest.upper())
        self.assertTrue(result["external_digest_match"])
        self.assertFalse(result["production_ready"])

    def test_independent_digest_mismatch_denied(self):
        with self.assertRaises(BackupError) as exc:
            validate_snapshot(self.file, expected_sha256="0" * 64)
        self.assertEqual("SNAPSHOT_SHA256_MISMATCH", exc.exception.code)

    def test_malformed_independent_digest_denied(self):
        for invalid in ("", "not a sha", "z" * 64, "a" * 63, "a" * 65, 3):
            with self.subTest(invalid=invalid), self.assertRaises(BackupError) as exc:
                validate_snapshot(self.file, expected_sha256=invalid)
            self.assertEqual("INVALID_EXPECTED_SHA256", exc.exception.code)

    def test_cli_independent_digest_receipt(self):
        import hashlib
        digest = hashlib.sha256(self.file.read_bytes()).hexdigest()
        for received, code, expected in [
            (digest, 0, None),
            ("f" * 64 if digest != "f" * 64 else "0" * 64, 2, "SNAPSHOT_SHA256_MISMATCH")
        ]:
            output = StringIO()
            with contextlib.redirect_stdout(output):
                actual = main(["--snapshot", str(self.file), "--expected-sha256", received])
            self.assertEqual(code, actual)
            body = json.loads(output.getvalue())
            if expected is None:
                self.assertTrue(body["external_digest_match"])
            else:
                self.assertEqual(expected, body["error_code"])
            self.assertNotIn("TOP_SECRET_BACKUP", output.getvalue())

    def test_bad_header_denied(self):
        self.file.write_bytes(b"BAD_HEADER" * 20)
        with self.assertRaises(BackupError) as e:
            validate_snapshot(self.file)
        self.assertEqual("SNAPSHOT_NOT_SQLITE", e.exception.code)

    def test_missing_file_denied(self):
        with self.assertRaises(BackupError):
            validate_snapshot(self.root / "missing.db")

    def test_directory_denied(self):
        with self.assertRaises(BackupError):
            validate_snapshot(self.root)

    def test_wal_companion_appearing_during_hash_is_denied(self):
        # Reproduction: before this guard a late WAL left the database
        # digest and in-memory integrity unchanged, yielding a false PASS.
        wal = Path(str(self.file) + "-wal")
        original_hash = snapshot_module._sha256
        created = False

        def add_late_sidecar(path):
            nonlocal created
            if not created:
                created = True
                wal.write_bytes(b"late-sidecar-sentinel")
            return original_hash(path)

        with patch.object(snapshot_module, "_sha256", side_effect=add_late_sidecar):
            with self.assertRaises(BackupError) as caught:
                validate_snapshot(self.file)
        self.assertEqual("SNAPSHOT_HAS_COMPANION", caught.exception.code)
        self.assertEqual(b"late-sidecar-sentinel", wal.read_bytes())

    def test_wal_companion_denied_without_modification(self):
        wal = Path(str(self.file) + "-wal")
        wal.write_bytes(b"sentinel")
        with self.assertRaises(BackupError) as e:
            validate_snapshot(self.file)
        self.assertEqual("SNAPSHOT_HAS_COMPANION", e.exception.code)
        self.assertEqual(b"sentinel", wal.read_bytes())

    def test_dangling_wal_symlink_denied(self):
        wal = Path(str(self.file) + "-wal")
        try:
            wal.symlink_to(self.root / "absent.wal")
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation not permitted on this runner")
        self.assertFalse(wal.exists())
        self.assertTrue(wal.is_symlink())
        with self.assertRaises(BackupError) as e:
            validate_snapshot(self.file)
        self.assertEqual("SNAPSHOT_HAS_COMPANION", e.exception.code)

    def test_inaccessible_wal_metadata_is_not_treated_as_absent(self):
        # Python 3.14 pathlib exists/is_symlink may return False on ACL denial.
        # Simulate that behavior independently of the hosted Python version.
        wal = Path(str(self.file) + "-wal")
        original_lstat = Path.lstat

        def denied_wal_lstat(path):
            if path == wal:
                raise PermissionError("synthetic metadata access denied")
            return original_lstat(path)

        with (patch.object(Path, "exists", return_value=False),
              patch.object(Path, "is_symlink", return_value=False),
              patch.object(Path, "is_junction", return_value=False, create=True),
              patch.object(Path, "lstat", denied_wal_lstat)):
            with self.assertRaises(BackupError) as caught:
                validate_snapshot(self.file)
        self.assertEqual("SNAPSHOT_COMPANION_UNVERIFIABLE", caught.exception.code)

    def test_rollback_journal_denied(self):
        journal = Path(str(self.file) + "-journal")
        journal.write_bytes(b"sentinel")
        with self.assertRaises(BackupError):
            validate_snapshot(self.file)

    def test_valid_foreign_keys_pass(self):
        with contextlib.closing(sqlite3.connect(self.file)) as db:
            with db:
                db.execute("PRAGMA foreign_keys=ON")
                db.execute("CREATE TABLE parent(id INTEGER PRIMARY KEY)")
                db.execute("CREATE TABLE child(parent_id INTEGER REFERENCES parent(id))")
                db.execute("INSERT INTO parent(id) VALUES(1)")
                db.execute("INSERT INTO child(parent_id) VALUES(1)")
        result = validate_snapshot(self.file)
        self.assertEqual("PASS", result["foreign_key_integrity"])

    def test_orphan_foreign_key_is_denied_even_if_sqlite_integrity_is_ok(self):
        # SQLite's integrity_check can report 'ok' for an orphan foreign key.
        with contextlib.closing(sqlite3.connect(self.file)) as db:
            with db:
                db.execute("PRAGMA foreign_keys=OFF")
                db.execute("CREATE TABLE parent(id INTEGER PRIMARY KEY)")
                db.execute("CREATE TABLE child(parent_id INTEGER REFERENCES parent(id))")
                db.execute("INSERT INTO child(parent_id) VALUES(999)")
            self.assertEqual("ok", db.execute("PRAGMA integrity_check").fetchone()[0])
        with self.assertRaises(BackupError) as exc:
            validate_snapshot(self.file)
        self.assertEqual("SQLITE_FOREIGN_KEY_FAILED", exc.exception.code)

    def test_schema_missing_denied(self):
        blank = self.root / "blank.db"
        with contextlib.closing(sqlite3.connect(blank)) as conn:
            conn.execute("PRAGMA user_version=1")
        with self.assertRaises(BackupError) as e:
            validate_snapshot(blank)
        self.assertEqual("SQLITE_SCHEMA_EMPTY", e.exception.code)

    def test_oversize_denied_without_loading(self):
        with self.file.open("r+b") as stream:
            stream.truncate(MAX_BYTES + 1)
        with self.assertRaises(BackupError) as e:
            validate_snapshot(self.file)
        self.assertEqual("SNAPSHOT_SIZE_OUT_OF_BOUNDS", e.exception.code)

    def test_corrupt_source_not_modified(self):
        corrupt = self.file.read_bytes()[:32] + b"\x00" * 200
        self.file.write_bytes(corrupt)
        with self.assertRaises(BackupError):
            validate_snapshot(self.file)
        self.assertEqual(corrupt, self.file.read_bytes())


    def test_symlinked_parent_directory_denied(self):
        # A directory alias can silently redirect an apparent offline snapshot.
        alias = self.root / "offline-backup-alias"
        try:
            alias.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation not permitted on this runner")
        with self.assertRaises(BackupError) as caught:
            validate_snapshot(alias / self.file.name)
        self.assertEqual("SNAPSHOT_PARENT_REDIRECTED", caught.exception.code)

    def test_parent_redirected_after_first_hash_is_denied_simulated(self):
        # A late parent symlink can preserve the same file inode and digest.
        # Final-file is_symlink() alone cannot detect this redirection.
        original_hash = snapshot_module._sha256
        original_is_symlink = Path.is_symlink
        first_hash_done = False

        def hash_then_redirect(path):
            nonlocal first_hash_done
            value = original_hash(path)
            first_hash_done = True
            return value

        def redirected_parent(path):
            return (first_hash_done and path == self.root) or original_is_symlink(path)

        with (patch.object(Path, "is_symlink", redirected_parent),
              patch.object(snapshot_module, "_sha256", side_effect=hash_then_redirect)):
            with self.assertRaises(BackupError) as caught:
                validate_snapshot(self.file)
        self.assertEqual("SNAPSHOT_CHANGED_DURING_CHECK", caught.exception.code)

    def test_parent_replaced_with_symlink_to_same_inode_denied(self):
        offline = self.root / "offline"
        offline.mkdir()
        backup = offline / "backup.db"
        backup.write_bytes(self.file.read_bytes())
        moved = self.root / "moved"
        original_hash = snapshot_module._sha256
        switched = False

        def replace_parent_then_hash(path):
            nonlocal switched
            if not switched:
                switched = True
                offline.rename(moved)
                try:
                    offline.symlink_to(moved, target_is_directory=True)
                except (OSError, NotImplementedError):
                    self.skipTest("Directory symlink creation not permitted")
            return original_hash(path)

        with patch.object(snapshot_module, "_sha256", side_effect=replace_parent_then_hash):
            with self.assertRaises(BackupError) as caught:
                validate_snapshot(backup)
        self.assertEqual("SNAPSHOT_CHANGED_DURING_CHECK", caught.exception.code)


    def test_hardlink_alias_to_active_fixture_denied(self):
        # Hard links evade is_symlink(), but do not represent separate backups.
        alias = self.root / "offline-copy.db"
        try:
            os.link(self.file, alias)
        except (OSError, NotImplementedError):
            self.skipTest("Hardlink creation not permitted on this runner")
        self.assertFalse(alias.is_symlink())
        self.assertGreater(alias.stat().st_nlink, 1)
        original = self.file.read_bytes()
        with self.assertRaises(BackupError) as caught:
            validate_snapshot(alias)
        self.assertEqual("SNAPSHOT_HARDLINKED", caught.exception.code)
        self.assertEqual(original, self.file.read_bytes())

    def test_separate_copy_not_mistaken_for_hardlink(self):
        copy = self.root / "independent-copy.db"
        copy.write_bytes(self.file.read_bytes())
        self.assertEqual(1, copy.stat().st_nlink)
        self.assertEqual("PASS", validate_snapshot(copy)["sqlite_integrity"])

    def test_windows_junction_parent_denied_simulated(self):
        # Path.is_junction is available on supported newer Python/Windows.
        from unittest.mock import patch
        original = getattr(Path, "is_junction", lambda path: False)
        def is_junction(path):
            return path == self.root or original(path)
        with patch.object(Path, "is_junction", is_junction, create=True):
            with self.assertRaises(BackupError) as caught:
                validate_snapshot(self.file)
        self.assertEqual("SNAPSHOT_PARENT_REDIRECTED", caught.exception.code)


    def test_replacement_before_first_hash_denied(self):
        # Original validator silently accepted a different, same-size valid DB
        # swapped after its initial stat() but before the first SHA-256.
        replacement = self.root / "replacement.db"
        with contextlib.closing(sqlite3.connect(replacement)) as db:
            with db:
                db.execute("CREATE TABLE sample(id INTEGER PRIMARY KEY, secret TEXT)")
                db.execute("INSERT INTO sample(secret) VALUES(?)", ("ANOTHER_FIXTURE_VALUE",))
        self.assertEqual(self.file.stat().st_size, replacement.stat().st_size)
        original_identity = (self.file.stat().st_dev, self.file.stat().st_ino)
        original_hash = snapshot_module._sha256
        swapped = False

        def replace_then_hash(path):
            nonlocal swapped
            if not swapped:
                swapped = True
                os.replace(replacement, self.file)
            return original_hash(path)

        with patch.object(snapshot_module, "_sha256", side_effect=replace_then_hash):
            with self.assertRaises(BackupError) as caught:
                validate_snapshot(self.file)
        self.assertEqual("SNAPSHOT_CHANGED_DURING_CHECK", caught.exception.code)
        self.assertNotEqual(original_identity, (self.file.stat().st_dev, self.file.stat().st_ino))

    def test_hardlink_created_after_precheck_denied(self):
        # A new hard link after st_nlink==1 precheck must not pass silently.
        alias = self.root / "late-hardlink.db"
        original_hash = snapshot_module._sha256
        linked = False

        def link_then_hash(path):
            nonlocal linked
            if not linked:
                linked = True
                try:
                    os.link(self.file, alias)
                except (OSError, NotImplementedError):
                    self.skipTest("Hardlink creation not permitted on this runner")
            return original_hash(path)

        with patch.object(snapshot_module, "_sha256", side_effect=link_then_hash):
            with self.assertRaises(BackupError) as caught:
                validate_snapshot(self.file)
        self.assertEqual("SNAPSHOT_CHANGED_DURING_CHECK", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
