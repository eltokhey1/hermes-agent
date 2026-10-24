#!/usr/bin/env python3
"""No-write SQLite backup preflight; does not prove Hermes functional restore."""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from urllib.parse import quote

SCHEMA = "hermes.owner.sqlite_memory_preflight.v1"
MAX_BYTES = 512 * 1024 * 1024
HEADER = b"SQLite format 3\x00"


class BackupError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as reader:
        for chunk in iter(lambda: reader.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def _same_snapshot_identity(snapshot: Path, initial: os.stat_result) -> bool:
    """Fail closed on detected file replacement, symlink swap, or rewrite.

    This is a consistency preflight, not a race-free file-handle pin.
    """
    try:
        current = snapshot.stat()
        return (not snapshot.is_symlink() and current.st_nlink == 1 and
                initial.st_ino != 0 and current.st_ino != 0 and
                (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns) ==
                (initial.st_dev, initial.st_ino, initial.st_size, initial.st_mtime_ns))
    except OSError:
        return False


def _reject_companions(snapshot: Path) -> None:
    """Reject WAL/SHM/journal sidecars, including dangling symlinks/junctions."""
    for ext in ("-wal", "-shm", "-journal"):
        companion = Path(str(snapshot) + ext)
        # Python 3.14 pathlib predicates return False on inaccessible paths.
        # lstat sees dangling links/reparse points and propagates ACL failures.
        try:
            companion.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise BackupError("SNAPSHOT_COMPANION_UNVERIFIABLE") from exc
        # Any sidecar, including a late WAL/journal or dangling link, is unsafe.
        raise BackupError("SNAPSHOT_HAS_COMPANION")


def validate_snapshot(snapshot: Path, *, expected_sha256: str | None = None) -> dict:
    """Validate a stable offline snapshot, never an active Hermes state.db."""
    # A redirected parent can bypass the final-file symlink check and silently
    # turn an "offline backup" argument into a path to a live Hermes database.
    # Reject symlinks and Windows junctions in the entire supplied parent chain.
    for parent in snapshot.parents:
        try:
            junction = getattr(parent, "is_junction", None)
            if parent.is_symlink() or (junction is not None and junction()):
                raise BackupError("SNAPSHOT_PARENT_REDIRECTED")
        except OSError as exc:
            raise BackupError("SNAPSHOT_PARENT_UNVERIFIABLE") from exc
    if snapshot.is_symlink() or not snapshot.is_file():
        raise BackupError("SNAPSHOT_NOT_REGULAR_FILE")
    stat = snapshot.stat()
    # A hard link is a regular file, not a symlink. Without this guard an
    # apparent offline copy can be another name for the live state.db inode.
    # This is only a preflight check; it cannot certify an off-device backup.
    if stat.st_nlink != 1:
        raise BackupError("SNAPSHOT_HARDLINKED")
    if stat.st_ino == 0:
        raise BackupError("SNAPSHOT_IDENTITY_UNAVAILABLE")
    size = stat.st_size
    if not len(HEADER) <= size <= MAX_BYTES:
        raise BackupError("SNAPSHOT_SIZE_OUT_OF_BOUNDS")
    # A separate WAL/journal might contain uncheckpointed committed changes.
    _reject_companions(snapshot)
    with snapshot.open("rb") as source:
        if source.read(len(HEADER)) != HEADER:
            raise BackupError("SNAPSHOT_NOT_SQLITE")
    if expected_sha256 is not None:
        if (not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or
                any(c not in "0123456789abcdefABCDEF" for c in expected_sha256)):
            raise BackupError("INVALID_EXPECTED_SHA256")
        expected_sha256 = expected_sha256.lower()
    before = _sha256(snapshot)
    if not _same_snapshot_identity(snapshot, stat):
        raise BackupError("SNAPSHOT_CHANGED_DURING_CHECK")
    # Reject a structurally healthy SQLite file that is not the recorded backup.
    if expected_sha256 is not None and before != expected_sha256:
        raise BackupError("SNAPSHOT_SHA256_MISMATCH")
    uri = "file:" + quote(snapshot.resolve().as_posix(), safe="/:") + "?immutable=1"
    try:
        with closing(sqlite3.connect(uri, uri=True, timeout=3)) as source:
            with closing(sqlite3.connect(":memory:", timeout=3)) as restored:
                source.backup(restored, pages=128, sleep=0)
                check = [row[0] for row in restored.execute("PRAGMA integrity_check")]
                if check != ["ok"]:
                    raise BackupError("SQLITE_INTEGRITY_FAILED")
                tables = restored.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
                ).fetchone()[0]
                if tables < 1:
                    raise BackupError("SQLITE_SCHEMA_EMPTY")
                # SQLite integrity_check alone does not detect broken FOREIGN KEY
                # relationships. Check the restored snapshot independently.
                if restored.execute("PRAGMA foreign_key_check").fetchone() is not None:
                    raise BackupError("SQLITE_FOREIGN_KEY_FAILED")
                pages = restored.execute("PRAGMA page_count").fetchone()[0]
    except sqlite3.Error as exc:
        raise BackupError("SQLITE_MEMORY_RESTORE_FAILED") from exc
    if (not _same_snapshot_identity(snapshot, stat) or
            _sha256(snapshot) != before or
            not _same_snapshot_identity(snapshot, stat)):
        raise BackupError("SNAPSHOT_CHANGED_DURING_CHECK")
    # The initial sidecar check is not sufficient: another process may
    # create a WAL/journal while hashing or restoring the snapshot.
    _reject_companions(snapshot)
    return {
        "schema": SCHEMA,
        "mode": "READ_ONLY_MEMORY_RESTORE",
        "snapshot_sha256": before,
        "external_digest_match": True if expected_sha256 is not None else None,
        "snapshot_bytes": size,
        "restored_page_count": pages,
        "restored_table_count": tables,
        "sqlite_integrity": "PASS",
        "foreign_key_integrity": "PASS",
        "hermes_functional_restore": "NOT_TESTED",
        "owner_windows_p0": "UNVERIFIED",
        "production_ready": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect an operator-created offline SQLite backup")
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--expected-sha256", help="Independent 64-digit SHA-256 of offline backup")
    args = parser.parse_args(argv)
    try:
        report, code = validate_snapshot(args.snapshot, expected_sha256=args.expected_sha256), 0
    except BackupError as exc:
        report, code = {"schema": SCHEMA, "status": "NO_GO", "error_code": exc.code,
                        "production_ready": False}, 2
    except Exception:
        report, code = {"schema": SCHEMA, "status": "NO_GO",
                        "error_code": "UNEXPECTED_ERROR", "production_ready": False}, 2
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
