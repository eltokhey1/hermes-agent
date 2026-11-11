"""Synthetic-only verification of independent HMAC checkpoint prototype.

Requires independent key and monotonic epoch in an actual deployment; here the
key is fake and exists in the runner exclusively to prove the algorithm.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sqlite3

import pytest


SOURCE = os.environ["PR10_SOURCE_SCRIPT"]
srcspec = importlib.util.spec_from_file_location("pr10_pinned_source", SOURCE)
si = importlib.util.module_from_spec(srcspec)
srcspec.loader.exec_module(si)

protospec = importlib.util.spec_from_file_location(
    "pr10_anchor_research", Path(__file__).with_name("pr10_external_anchor_prototype.py")
)
anchor = importlib.util.module_from_spec(protospec)
protospec.loader.exec_module(anchor)

KEY = b"non-secret-synthetic-anchor-test-key-2026"
WRONG_KEY = b"deliberately-wrong-synthetic-key-2026"
SRC = "https://example.org/synthetic-carrier"
CONTAINER = "ABCD1234567"


def record(event_id="native-1", code="GTIN", when="2026-10-18T08:00:00Z"):
    return {
        "eventID": event_id,
        "eventType": "EQUIPMENT",
        "equipmentReference": CONTAINER,
        "equipmentEventTypeCode": code,
        "eventClassifierCode": "ACT",
        "eventDateTime": when,
        "eventCreatedDateTime": "2026-10-18T09:00:00Z"
    }


def populated(tmp_path):
    db = si.connect(tmp_path / "evidence.sqlite")
    si.ingest(db, [si.adapt_dcsa(record(), "carrier", SRC)])
    receipt = anchor.issue_checkpoint(db, independent_key=KEY, epoch=1)
    return db, receipt


def verify(db, receipt, epoch=1, key=KEY):
    return anchor.verify_checkpoint(
        db, independent_key=key, checkpoint=receipt,
        minimum_expected_epoch=epoch
    )


def test_genuine_signed_state_verifies(tmp_path):
    db, receipt = populated(tmp_path)
    verify(db, receipt)
    db.close()


def test_db_event_deletion_detected_by_independent_count_and_root(tmp_path):
    db, receipt = populated(tmp_path)
    db.execute("DELETE FROM evidence_events WHERE event_id='carrier:native-1'")
    db.commit()
    with pytest.raises(anchor.IntegrityError, match="differs"):
        verify(db, receipt)
    db.close()


def test_rehashing_modified_event_still_rejected_by_external_anchor(tmp_path):
    db, receipt = populated(tmp_path)
    db.execute("UPDATE evidence_events SET code='DISC' WHERE event_id='carrier:native-1'")
    field_names = anchor.FIELDS
    row = db.execute(
        f"SELECT {','.join(field_names)},payload_json FROM evidence_events WHERE event_id=?",
        ("carrier:native-1",)
    ).fetchone()
    event = dict(zip(field_names, row[:-1]))
    new_hash = si.digest({"event": event, "payload": json.loads(row[-1])})
    db.execute("UPDATE evidence_events SET record_sha256=? WHERE event_id='carrier:native-1'", (new_hash,))
    db.commit()
    assert si.evidence_report(db, CONTAINER, "2026-10-18T10:00:00Z")["shipment_state"] == "CURRENT_ACTUAL"
    with pytest.raises(anchor.IntegrityError, match="differs"):
        verify(db, receipt)
    db.close()


def test_forged_checkpoint_root_fails_hmac(tmp_path):
    db, receipt = populated(tmp_path)
    forged = {**receipt, "root": "0" * 64}
    with pytest.raises(anchor.IntegrityError, match="authentication"):
        verify(db, forged)
    db.close()


def test_wrong_key_fails_hmac(tmp_path):
    db, receipt = populated(tmp_path)
    with pytest.raises(anchor.IntegrityError, match="authentication"):
        verify(db, receipt, key=WRONG_KEY)
    db.close()


def test_old_valid_checkpoint_rejected_if_independent_epoch_is_newer(tmp_path):
    db, receipt_v1 = populated(tmp_path)
    saved = sqlite3.connect(tmp_path / "old_snapshot.sqlite")
    db.backup(saved)
    saved.close()
    si.ingest(db, [si.adapt_dcsa(
        record("native-2", "GTOT", "2026-10-18T08:30:00Z"), "carrier", SRC
    )])
    receipt_v2 = anchor.issue_checkpoint(db, independent_key=KEY, epoch=2)
    verify(db, receipt_v2, epoch=2)
    old = sqlite3.connect(tmp_path / "old_snapshot.sqlite")
    with pytest.raises(anchor.IntegrityError, match="rollback"):
        verify(old, receipt_v1, epoch=2)
    old.close()
    db.close()


def test_uncommitted_write_does_not_change_signed_state(tmp_path):
    db, receipt = populated(tmp_path)
    db.execute("BEGIN IMMEDIATE")
    db.execute("UPDATE evidence_events SET code='DISC' WHERE event_id='carrier:native-1'")
    db.rollback()
    verify(db, receipt)
    db.close()
