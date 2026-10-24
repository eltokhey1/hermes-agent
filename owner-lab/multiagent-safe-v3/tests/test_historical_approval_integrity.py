"""Synthetic regression cases: signed approval evidence must match durable receipts.

No real identity provider, network, shell, production data or real external action.
"""
from contextlib import closing
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from approvals import ApprovalDenied, ApprovalIssuer, ApprovalVerifier
from orchestrator import GateError, HermesReference, canonical, digest
from test_secure_orchestrator import Clock, spec


class HistoricalApprovalIntegrityTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "approval.sqlite"
        self.clock = Clock()
        key = b"synthetic-only-approval-test-key-32bytes"
        self.issuer = ApprovalIssuer(key, clock=self.clock)
        self.verifier = ApprovalVerifier(key, clock=self.clock)
        self.h = HermesReference(self.path, verifier=self.verifier)

    def approved(self, *, idem="test", approver="owner-demo"):
        task = self.h.submit(spec("demo.review"), idempotency_key=idem)
        self.h.prepare(task)
        token = self.issuer.issue(task_id=task, spec_hash=self.h.task(task)["spec_hash"],
                                  approver=approver, decision="approve", ttl_seconds=30)
        self.h.approve(task, token)
        return task, token

    def overwrite_token(self, task, token):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE tasks SET approval_assertion=? WHERE task_id=?", (token, task))

    def test_valid_signature_and_receipt_are_certified(self):
        task, _ = self.approved()
        self.assertTrue(self.h.verify_ledger())
        self.assertEqual("SUCCEEDED", self.h.execute_demo(task) and self.h.task(task)["state"])

    def test_modified_signature_is_denied_before_reservation(self):
        task, token = self.approved()
        self.overwrite_token(task, token[:-1] + ("A" if token[-1] != "A" else "B"))
        self.assertFalse(self.h.verify_ledger())
        with self.assertRaises(GateError):
            self.h.reserve(task)

    def test_random_assertion_string_is_denied(self):
        task, _ = self.approved()
        self.overwrite_token(task, "not-a-signed-approval")
        self.assertFalse(self.h.verify_ledger())

    def test_signed_token_with_different_nonce_is_denied(self):
        task, _ = self.approved()
        replacement = self.issuer.issue(task_id=task, spec_hash=self.h.task(task)["spec_hash"],
                                        approver="owner-demo", decision="approve")
        self.overwrite_token(task, replacement)
        self.assertFalse(self.h.verify_ledger())

    def test_token_bound_to_another_task_is_denied(self):
        first, first_token = self.approved(idem="first")
        second, second_token = self.approved(idem="second")
        self.overwrite_token(first, second_token)
        self.assertFalse(self.h.verify_ledger())
        self.overwrite_token(first, first_token)
        self.assertTrue(self.h.verify_ledger())

    def test_historical_expiry_does_not_corrupt_record(self):
        task, token = self.approved()
        spec_hash = self.h.task(task)["spec_hash"]
        self.clock.t += 31
        claims = self.verifier.inspect_historical(token, task_id=task, spec_hash=spec_hash)
        self.assertEqual("approve", claims["decision"])
        self.assertTrue(self.h.verify_ledger())
        with self.assertRaises(ApprovalDenied):
            self.verifier.verify(token, task_id=task, spec_hash=spec_hash)
        with self.assertRaises(GateError):
            self.h.reserve(task)

    def test_forged_ledger_approver_with_rehashed_event_is_denied(self):
        self.approved()
        with closing(sqlite3.connect(self.path)) as db, db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM events WHERE event_type='APPROVAL_DECISION'").fetchone()
            payload = json.loads(row["payload"])
            payload["approver"] = "forged-owner"
            body = {"task_id": row["task_id"], "event_type": row["event_type"],
                    "payload": payload, "previous_hash": row["previous_hash"],
                    "timestamp": row["timestamp"]}
            db.execute("UPDATE events SET payload=?,event_hash=? WHERE seq=?",
                       (canonical(payload), digest(body), row["seq"]))
        self.assertFalse(self.h.verify_ledger())


if __name__ == "__main__":
    unittest.main()
