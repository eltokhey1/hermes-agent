#!/usr/bin/env python3
"""No-write SQLite backup preflight; does not prove Hermes functional restore."""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
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


def validate_snapshot(snapshot: Path) -> dict:
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
    size = snapshot.stat().st_size
    if not len(HEADER) <= size <= MAX_BYTES:
        raise BackupError("SNAPSHOT_SIZE_OUT_OF_BOUNDS")
    # A separate WAL/journal might contain uncheckpointed committed changes.
    for ext in ("-wal", "-shm", "-journal"):
        companion = Path(str(snapshot) + ext)
        # Reject dangling symlinks too: exists() alone misses them.
        if companion.exists() or companion.is_symlink():
            raise BackupError("SNAPSHOT_HAS_COMPANION")
    with snapshot.open("rb") as source:
        if source.read(len(HEADER)) != HEADER:
            raise BackupError("SNAPSHOT_NOT_SQLITE")
    before = _sha256(snapshot)
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
    if _sha256(snapshot) != before or snapshot.stat().st_size != size:
        raise BackupError("SNAPSHOT_CHANGED_DURING_CHECK")
    return {
        "schema": SCHEMA,
        "mode": "READ_ONLY_MEMORY_RESTORE",
        "snapshot_sha256": before,
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
    args = parser.parse_args(argv)
    try:
        report, code = validate_snapshot(args.snapshot), 0
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
