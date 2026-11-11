"""RESEARCH-ONLY illustration of independently MAC-anchored SQLite evidence.

This does NOT modify Shipment Intelligence. The HMAC key and monotonic epoch
must be held by an independent trust root, outside agent and DB write access.
An attacker who controls both that root and the DB can still forge evidence.
An authentic carrier API signature is a different security property.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3


class IntegrityError(ValueError):
    pass


FIELDS = (
    "event_id", "category", "subject_type", "subject_id", "code",
    "classifier", "occurred_utc", "reported_local",
    "source_url", "source_name", "location"
)
COLUMNS = (*FIELDS, "payload_json", "record_sha256")


def _canonical(data: object) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _db_state(conn: sqlite3.Connection) -> dict:
    # Whitelisted static columns only.
    rows = conn.execute(
        f"SELECT {','.join(COLUMNS)} FROM evidence_events ORDER BY event_id"
    ).fetchall()
    evidence = []
    for row in rows:
        stored = dict(zip(COLUMNS, row))
        try:
            payload = json.loads(stored["payload_json"])
            if not isinstance(payload, dict):
                raise IntegrityError("invalid payload type")
            ev = {name: stored[name] for name in FIELDS}
            computed = hashlib.sha256(_canonical({"event": ev, "payload": payload})).hexdigest()
            original = stored["record_sha256"]
            if not isinstance(original, str) or not hmac.compare_digest(computed, original):
                raise IntegrityError("row digest mismatch")
        except (ValueError, TypeError) as exc:
            raise IntegrityError("EVIDENCE_INTEGRITY: invalid persisted event") from exc
        evidence.append((stored["event_id"], stored["record_sha256"]))
    return {
        "count": len(evidence),
        "root": hashlib.sha256(_canonical(evidence)).hexdigest(),
    }


def issue_checkpoint(conn: sqlite3.Connection, *, independent_key: bytes, epoch: int) -> dict:
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1:
        raise ValueError("epoch must be a positive integer")
    if len(independent_key) < 32:
        raise ValueError("test signer key must be >= 32 bytes")
    signed = {"version": 1, "epoch": epoch, **_db_state(conn)}
    return {
        **signed,
        "mac": hmac.new(independent_key, _canonical(signed), hashlib.sha256).hexdigest(),
    }


def verify_checkpoint(conn: sqlite3.Connection, *, independent_key: bytes, checkpoint: dict,
                      minimum_expected_epoch: int) -> None:
    if not isinstance(checkpoint, dict):
        raise IntegrityError("checkpoint missing")
    signed = {name: checkpoint.get(name) for name in ("version", "epoch", "count", "root")}
    signature = checkpoint.get("mac")
    if signed["version"] != 1 or not isinstance(signature, str):
        raise IntegrityError("invalid checkpoint shape")
    if not isinstance(signed["epoch"], int) or isinstance(signed["epoch"], bool):
        raise IntegrityError("invalid checkpoint epoch")
    if signed["epoch"] < minimum_expected_epoch:
        raise IntegrityError("checkpoint rollback detected by independent expected epoch")
    if len(independent_key) < 32:
        raise IntegrityError("missing independent trust key")
    expected = hmac.new(independent_key, _canonical(signed), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise IntegrityError("checkpoint authentication failed")
    actual = _db_state(conn)
    if actual["count"] != signed["count"] or not hmac.compare_digest(actual["root"], str(signed["root"])):
        raise IntegrityError("database differs from independently signed checkpoint")
