"""Offline lab only: independently preserved event head detects whole-DB rewrites.

No actual external audit sink, no real identity, Windows host, or production.
"""
from contextlib import closing
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from approvals import ApprovalVerifier
from orchestrator import HermesReference, canonical, digest
from test_secure_orchestrator import Clock, spec


class IndependentAnchorTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "synthetic.sqlite"
        self.h = HermesReference(
            self.path, verifier=ApprovalVerifier(b"synthetic-only-approval-test-key-32bytes",
                                                clock=Clock())
        )

    def receipt(self):
        snap = self.h.status_summary()
        return snap["last_event_seq"], snap["ledger_head_unanchored"]

    def test_genesis_anchor(self):
        self.assertTrue(self.h.verify_external_anchor(expected_seq=0, expected_hash="GENESIS"))
        self.assertFalse(self.h.verify_external_anchor(expected_seq=1, expected_hash="0" * 64))

    def test_matching_and_stale_receipt(self):
        self.h.submit(spec(), idempotency_key="alpha")
        seq, head = self.receipt()
        self.assertTrue(self.h.verify_external_anchor(expected_seq=seq, expected_hash=head))
        self.h.submit(spec(), idempotency_key="beta")
        self.assertFalse(self.h.verify_external_anchor(expected_seq=seq, expected_hash=head))
        next_seq, next_head = self.receipt()
        self.assertTrue(self.h.verify_external_anchor(expected_seq=next_seq, expected_hash=next_head))

    def test_rehashed_event_without_anchored_receipt_is_detected(self):
        task = self.h.submit(spec(), idempotency_key="rewrite")
        seq, head = self.receipt()
        with closing(sqlite3.connect(self.path)) as db, db:
            db.row_factory = sqlite3.Row
            event = db.execute("SELECT * FROM events WHERE task_id=?", (task,)).fetchone()
            forged_timestamp = "2001-01-01T00:00:00+00:00"
            body = {
                "task_id": event["task_id"], "event_type": event["event_type"],
                "payload": json.loads(event["payload"]),
                "previous_hash": event["previous_hash"], "timestamp": forged_timestamp,
            }
            db.execute("UPDATE events SET timestamp=?,event_hash=? WHERE seq=?",
                       (forged_timestamp, digest(body), seq))
        self.assertTrue(self.h.verify_ledger(), "DB-local hash chain is forgeable")
        self.assertFalse(self.h.verify_external_anchor(expected_seq=seq, expected_hash=head))

    def test_whole_tail_and_task_deleted_is_detected(self):
        task = self.h.submit(spec(), idempotency_key="first")
        self.h.prepare(task)
        later = self.h.submit(spec(), idempotency_key="second")
        original_seq, original_head = self.receipt()
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("DELETE FROM events WHERE task_id=?", (later,))
            db.execute("DELETE FROM tasks WHERE task_id=?", (later,))
        self.assertTrue(self.h.verify_ledger(), "Remaining valid prefix is self-consistent")
        self.assertFalse(self.h.verify_external_anchor(expected_seq=original_seq,
                                                       expected_hash=original_head))

    def test_tampered_event_fails_both(self):
        task = self.h.submit(spec(), idempotency_key="tamper")
        seq, head = self.receipt()
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE events SET event_hash='tampered' WHERE task_id=?", (task,))
        self.assertFalse(self.h.verify_ledger())
        self.assertFalse(self.h.verify_external_anchor(expected_seq=seq, expected_hash=head))

    def test_malformed_anchor_inputs_fail_closed(self):
        for seq, head in [
            (True, "GENESIS"), (False, "GENESIS"), (-1, "GENESIS"),
            (1.0, "a" * 64), (0, "a" * 64), (1, "GENESIS"),
            (1, "A" * 64), (1, "not-a-sha"), (1, ""),
            (1, None), (0, None),
        ]:
            with self.subTest(seq=seq, head=head):
                self.assertFalse(self.h.verify_external_anchor(expected_seq=seq,
                                                                expected_hash=head))


if __name__ == "__main__":
    unittest.main()
