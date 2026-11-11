"""Independent PR10 acceptance v2: reject tampered evidence by raising or refusing status.

V1 red-run archived unchanged. This v2 explicitly requires an EVIDENCE_INTEGRITY
exception for damaged SQLite evidence; raising is safer than returning a status.
SOURCE is supplied by a SHA-pinned CI checkout; tests do not modify source.
"""
from __future__ import annotations

import importlib.util
import json
import os

import pytest

spec = importlib.util.spec_from_file_location(
    "independent_pr10_source", os.environ["PR10_SOURCE_SCRIPT"]
)
si = importlib.util.module_from_spec(spec)
spec.loader.exec_module(si)

SRC = "https://example.org/synthetic-evidence"
CONTAINER = "ABCD1234567"
NOW = "2026-10-18T10:00:00Z"


def dcsa(code="GTIN", event_id="evidence-1", classifier="ACT"):
    return {
        "eventID": event_id,
        "eventType": "EQUIPMENT",
        "equipmentReference": CONTAINER,
        "equipmentEventTypeCode": code,
        "eventClassifierCode": classifier,
        "eventDateTime": "2026-10-18T08:00:00Z",
        "eventCreatedDateTime": "2026-10-18T09:00:00Z",
    }


def populated(tmp_path):
    path = tmp_path / "events.sqlite"
    db = si.connect(path)
    si.ingest(db, [si.adapt_dcsa(dcsa(), "carrier", SRC)])
    return db, path


def assert_integrity_refused(db):
    with pytest.raises(ValueError, match="EVIDENCE_INTEGRITY"):
        si.evidence_report(db, CONTAINER, NOW)


def test_clean_control_current(tmp_path):
    db, _ = populated(tmp_path)
    assert si.evidence_report(db, CONTAINER, NOW)["shipment_state"] == "CURRENT_ACTUAL"


def test_reimport_is_idempotent(tmp_path):
    db, _ = populated(tmp_path)
    assert si.ingest(db, [si.adapt_dcsa(dcsa(), "carrier", SRC)])["duplicates"] == 1


def test_conflicting_native_event_id_fails_closed(tmp_path):
    db, _ = populated(tmp_path)
    with pytest.raises(ValueError, match="CONFLICT"):
        si.ingest(db, [si.adapt_dcsa(dcsa(code="DISC"), "carrier", SRC)])


def test_ais_never_creates_container_status(tmp_path):
    db = si.connect(tmp_path / "ais.sqlite")
    rec = {"record_id": "ais-1", "imo": 9173355,
           "event_type": "POSITION", "time_utc": "2026-10-18T09:00:00Z",
           "lat": 32.5, "lon": 14.2, "source_url": SRC}
    si.ingest(db, [si.adapt_ais(rec, "ais")])
    assert si.evidence_report(db, CONTAINER, NOW)["shipment_state"] == "UNKNOWN"


def test_native_provider_event_id_required():
    rec = dcsa()
    del rec["eventID"]
    with pytest.raises(ValueError, match="provider event id"):
        si.adapt_dcsa(rec, "carrier", SRC)


def test_modified_sqlite_event_code_raises_integrity_error(tmp_path):
    db, _ = populated(tmp_path)
    db.execute("UPDATE evidence_events SET code='DISC' WHERE event_id='carrier:evidence-1'")
    db.commit()
    assert_integrity_refused(db)


def test_modified_sqlite_payload_raises_integrity_error(tmp_path):
    db, _ = populated(tmp_path)
    db.execute("UPDATE evidence_events SET payload_json='{}' WHERE event_id='carrier:evidence-1'")
    db.commit()
    assert_integrity_refused(db)


@pytest.mark.parametrize("value", [True, False])
def test_boolean_ais_coordinate_rejected(value):
    rec = {"record_id": "ais-bool", "imo": 9173355, "event_type": "POSITION",
           "time_utc": "2026-10-18T09:00:00Z",
           "lat": value, "lon": 14.2, "source_url": SRC}
    with pytest.raises(ValueError, match="AIS"):
        si.adapt_ais(rec, "ais")


def test_tampered_ais_position_is_rejected_before_display(tmp_path):
    db = si.connect(tmp_path / "ais.sqlite")
    rec = {"record_id": "ais-1", "imo": 9173355,
           "event_type": "POSITION", "time_utc": "2026-10-18T09:00:00Z",
           "lat": 32.5, "lon": 14.2, "source_url": SRC}
    si.ingest(db, [si.adapt_ais(rec, "ais")])
    si.link(db, CONTAINER, "9173355", SRC,
            "Synthetic vessel association with independent document")
    db.execute("UPDATE evidence_events SET location='0, 0' WHERE event_id='ais:ais-1'")
    db.commit()
    assert_integrity_refused(db)


def test_malformed_persisted_payload_is_rejected(tmp_path):
    db, _ = populated(tmp_path)
    db.execute("UPDATE evidence_events SET payload_json='not-json' WHERE event_id='carrier:evidence-1'")
    db.commit()
    assert_integrity_refused(db)


def test_tampered_source_url_is_rejected(tmp_path):
    db, _ = populated(tmp_path)
    db.execute(
        "UPDATE evidence_events SET source_url='https://example.org/altered' "
        "WHERE event_id='carrier:evidence-1'"
    )
    db.commit()
    assert_integrity_refused(db)


def test_cli_fails_closed_with_exit_code_2(tmp_path, capsys):
    db, path = populated(tmp_path)
    db.execute("UPDATE evidence_events SET code='DISC' WHERE event_id='carrier:evidence-1'")
    db.commit()
    exit_code = si.main(["--db", str(path), "status", CONTAINER, "--now", NOW])
    assert exit_code == 2
    reported = json.loads(capsys.readouterr().err.strip())
    assert reported["status"] == "FAIL_CLOSED"
    assert "EVIDENCE_INTEGRITY" in reported["error"]
