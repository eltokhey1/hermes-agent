"""Independent PR #10 adversarial acceptance tests.

Not part of PR #10. Do not modify or rely on the author's original tests.
Tests import the exact pinned source checkout via PR10_SOURCE_SCRIPT.
All data is synthetic; no network/provider calls.
"""
from __future__ import annotations

import importlib.util
import os

import pytest


SOURCE = os.environ["PR10_SOURCE_SCRIPT"]
spec = importlib.util.spec_from_file_location("independently_checked_shipment_intelligence", SOURCE)
si = importlib.util.module_from_spec(spec)
spec.loader.exec_module(si)

SRC = "https://example.org/synthetic-provenance"
ID = "ABCD1234567"
NOW = "2026-10-18T10:00:00Z"


def record(event_id="proof-001", code="GTIN", classifier="ACT"):
    return {
        "eventID": event_id,
        "eventType": "EQUIPMENT",
        "equipmentReference": ID,
        "equipmentEventTypeCode": code,
        "eventClassifierCode": classifier,
        "eventDateTime": "2026-10-18T08:00:00Z",
        "eventCreatedDateTime": "2026-10-18T09:00:00Z",
    }


def db_with_one_event(tmp_path):
    db = si.connect(tmp_path / "receipt.sqlite")
    si.ingest(db, [si.adapt_dcsa(record(), "carrier", SRC)])
    return db


def test_control_baseline_has_expected_synthetic_status(tmp_path):
    db = db_with_one_event(tmp_path)
    assert si.evidence_report(db, ID, NOW)["shipment_state"] == "CURRENT_ACTUAL"


def test_replay_same_provider_record_is_idempotent(tmp_path):
    db = db_with_one_event(tmp_path)
    result = si.ingest(db, [si.adapt_dcsa(record(), "carrier", SRC)])
    assert result["inserted"] == 0 and result["duplicates"] == 1


def test_conflicting_native_event_id_is_fail_closed(tmp_path):
    db = db_with_one_event(tmp_path)
    with pytest.raises(ValueError, match="CONFLICT"):
        si.ingest(db, [si.adapt_dcsa(record(code="DISC"), "carrier", SRC)])


def test_a_vessel_position_cannot_prove_container_status(tmp_path):
    db = si.connect(tmp_path / "ais.sqlite")
    ais = {
        "record_id": "ais-123",
        "imo": 9173355,
        "event_type": "POSITION",
        "time_utc": "2026-10-18T09:00:00Z",
        "lat": 32.5, "lon": 14.2,
        "source_url": SRC
    }
    si.ingest(db, [si.adapt_ais(ais, "ais")])
    assert si.evidence_report(db, ID, NOW)["shipment_state"] == "UNKNOWN"


def test_native_provider_id_is_mandatory():
    bad = record()
    bad.pop("eventID")
    with pytest.raises(ValueError, match="provider event id"):
        si.adapt_dcsa(bad, "carrier", SRC)


def test_changed_persisted_event_code_must_not_be_trusted(tmp_path):
    """Stored record_sha256 must be checked before a status can claim CURRENT."""
    db = db_with_one_event(tmp_path)
    db.execute("UPDATE evidence_events SET code = 'DISC' WHERE event_id = 'carrier:proof-001'")
    db.commit()
    report = si.evidence_report(db, ID, NOW)
    assert report["shipment_state"] != "CURRENT_ACTUAL", (
        "Unsafe: an edited SQLite event code was accepted as verified CURRENT_ACTUAL"
    )


def test_changed_persisted_payload_must_not_be_trusted(tmp_path):
    """A valid-looking record with a mismatched original content hash is not proven."""
    db = db_with_one_event(tmp_path)
    db.execute("UPDATE evidence_events SET payload_json = ? WHERE event_id = 'carrier:proof-001'",
               ('{"forged":true}',))
    db.commit()
    report = si.evidence_report(db, ID, NOW)
    assert report["shipment_state"] != "CURRENT_ACTUAL", (
        "Unsafe: altered evidence payload was accepted without validating record_sha256"
    )


def test_boolean_coordinates_are_not_valid_ais_evidence():
    """Python bool is an int subclass; semantic latitude must reject True/False."""
    position = {
        "record_id": "ais-boolean",
        "imo": 9173355,
        "event_type": "POSITION",
        "time_utc": "2026-10-18T09:00:00Z",
        "lat": True,
        "lon": 14.2,
        "source_url": SRC,
    }
    with pytest.raises(ValueError, match="AIS"):
        si.adapt_ais(position, "ais")
