"""Independent adversarial resilience gates for PR10, no real provider access.

Source is injected by exact SHA in GitHub Actions. No code from this research
test is imported into the original shipping PR. RED tests intentionally expose
missing anti-deletion/rehash anchoring and nonconformant DCSA code validation.
The WAL and backup tests are synthetic SQLite-only, not owner Windows P0/P1.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest


spec = importlib.util.spec_from_file_location("pr10_pinned_resilience", os.environ["PR10_SOURCE_SCRIPT"])
si = importlib.util.module_from_spec(spec)
spec.loader.exec_module(si)

SRC = "https://example.org/synthetic-dcsa-source"
CONTAINER = "ABCD1234567"
NOW = "2026-10-18T10:00:00Z"


def dcsa(event_id="native-1", code="GTIN"):
    return {
        "eventID": event_id,
        "eventType": "EQUIPMENT",
        "equipmentReference": CONTAINER,
        "equipmentEventTypeCode": code,
        "eventClassifierCode": "ACT",
        "eventDateTime": "2026-10-18T08:00:00Z",
        "eventCreatedDateTime": "2026-10-18T09:00:00Z"
    }


def opened(tmp_path):
    db_path = tmp_path / "evidence.sqlite3"
    db = si.connect(db_path)
    assert si.ingest(db, [si.adapt_dcsa(dcsa(), "carrier", SRC)])["inserted"] == 1
    return db, db_path


def test_control_original_state_is_current(tmp_path):
    db, _ = opened(tmp_path)
    report = si.evidence_report(db, CONTAINER, NOW)
    assert report["shipment_state"] == "CURRENT_ACTUAL"
    assert report["latest_confirmed_equipment_event"]["code"] == "GTIN"


def test_unkeyed_digest_unchanged_row_tampering_is_rejected(tmp_path):
    db, _ = opened(tmp_path)
    db.execute("UPDATE evidence_events SET code='DISC' WHERE event_id='carrier:native-1'")
    db.commit()
    with pytest.raises(ValueError, match="EVIDENCE_INTEGRITY"):
        si.evidence_report(db, CONTAINER, NOW)


def test_deleted_event_detected_against_external_anchor(tmp_path):
    """RED expected: without external signed count/root, deletion becomes UNKNOWN."""
    db, _ = opened(tmp_path)
    db.execute("DELETE FROM evidence_events WHERE event_id='carrier:native-1'")
    db.commit()
    with pytest.raises(ValueError, match="EVIDENCE_INTEGRITY"):
        si.evidence_report(db, CONTAINER, NOW)


def test_recomputed_unkeyed_digest_cannot_make_tampering_trusted(tmp_path):
    """RED expected: a row rewrite plus rehash needs an independent trust root."""
    db, _ = opened(tmp_path)
    db.execute("UPDATE evidence_events SET code='DISC' WHERE event_id='carrier:native-1'")
    db.commit()
    fields = ("event_id", "category", "subject_type", "subject_id", "code",
              "classifier", "occurred_utc", "reported_local",
              "source_url", "source_name", "location")
    column_sql = ",".join(fields)
    row = db.execute(f"SELECT {column_sql}, payload_json FROM evidence_events WHERE event_id=?", 
                     ("carrier:native-1",)).fetchone()
    stored = dict(zip(fields, row[:len(fields)]))
    forged_hash = si.digest({"event": stored, "payload": json.loads(row[-1])})
    db.execute("UPDATE evidence_events SET record_sha256=? WHERE event_id='carrier:native-1'", (forged_hash,))
    db.commit()
    with pytest.raises(ValueError, match="EVIDENCE_INTEGRITY"):
        si.evidence_report(db, CONTAINER, NOW)


def test_nonstandard_dcsa_event_code_requires_conformance_review():
    """RED expected: syntactically legal tokens are not automatically DCSA codes."""
    with pytest.raises(ValueError):
        si.adapt_dcsa(dcsa(code="NOT_A_DCSA_EVENT_CODE"), "carrier", SRC)


def test_synthetic_sqlite_backup_restores_original_evidence(tmp_path):
    """SQLite backup API and separate restore path only; not Hermes P0."""
    db, original = opened(tmp_path)
    db.execute("PRAGMA journal_mode=WAL")
    saved = tmp_path / "isolated-backup.sqlite3"
    destination = sqlite3.connect(saved)
    try:
        db.backup(destination)
        assert destination.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        destination.close()
    db.execute("DELETE FROM evidence_events")
    db.commit()
    assert si.evidence_report(db, CONTAINER, NOW)["shipment_state"] == "UNKNOWN"
    restored = si.connect(saved)
    assert restored.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert si.evidence_report(restored, CONTAINER, NOW)["shipment_state"] == "CURRENT_ACTUAL"
    restored.close()
    db.close()


def test_simulated_sqlite_wal_crash_discards_uncommitted_edit(tmp_path):
    """Child-process os._exit simulates abrupt failure; not real P1 ESTOP/agent."""
    db, path = opened(tmp_path)
    assert db.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
    db.close()
    child = (
        "import os,sqlite3,sys\n"
        "db=sqlite3.connect(sys.argv[1])\n"
        "db.execute('BEGIN IMMEDIATE')\n"
        "db.execute(\"UPDATE evidence_events SET code='DISC' WHERE event_id='carrier:native-1'\")\n"
        "os._exit(77)\n"
    )
    result = subprocess.run([sys.executable, "-c", child, str(path)],
                            capture_output=True, timeout=20, check=False)
    assert result.returncode == 77
    recovered = si.connect(path)
    assert recovered.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert si.evidence_report(recovered, CONTAINER, NOW)["latest_confirmed_equipment_event"]["code"] == "GTIN"
    recovered.close()
