"""Synthetic-only SQLite fixtures; no real Hermes database access."""
import contextlib
from io import StringIO
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
