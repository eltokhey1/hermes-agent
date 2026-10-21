"""Negative tests: a valid hash chain alone must not certify stored task state."""
from contextlib import closing
import sqlite3
import tempfile
import json
import unittest
from pathlib import Path

from approvals import ApprovalIssuer, ApprovalVerifier
from orchestrator import GateError, HermesReference
from test_secure_orchestrator import Clock, spec


class DurableStateLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "lab.sqlite"
        self.clock = Clock()
        key = b"synthetic-only-approval-test-key-32bytes"
        self.issuer = ApprovalIssuer(key, clock=self.clock)
        self.h = HermesReference(self.db, verifier=ApprovalVerifier(key, clock=self.clock))

    def tamper(self, sql, args=()):
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.execute(sql, args)

    def test_state_forged_succeeded_without_execution(self):
        task = self.h.submit(spec(), idempotency_key="fake-done")
        self.tamper("UPDATE tasks SET state='SUCCEEDED' WHERE task_id=?", (task,))
        self.assertFalse(self.h.verify_ledger())

    def test_high_risk_ready_without_approval(self):
        task = self.h.submit(spec("demo.review"), idempotency_key="fake-authorized")
        self.h.prepare(task)
        self.tamper("UPDATE tasks SET state='READY' WHERE task_id=?", (task,))
        self.assertFalse(self.h.verify_ledger())

    def test_ledger_truncated_valid_prefix_is_not_accepted(self):
        task = self.h.submit(spec(), idempotency_key="truncated-tail")
        self.h.prepare(task)
        self.h.execute_demo(task)
        self.tamper("DELETE FROM events WHERE event_type='SUCCEEDED'")
        self.assertFalse(self.h.verify_ledger())

    def test_corrupted_spec_hash_is_not_certified(self):
        task = self.h.submit(spec(), idempotency_key="fake-hash")
        self.tamper("UPDATE tasks SET spec_hash=? WHERE task_id=?", ("f" * 64, task))
        self.assertFalse(self.h.verify_ledger())

    def test_orphan_validly_hashed_event_is_not_certified(self):
        self.h.submit(spec(), idempotency_key="original")
        with self.h._conn() as conn:
            conn.execute("BEGIN IMMEDIATE")
            self.h._event(conn, "does-not-exist", "PREPARED", {"state": "READY"})
        self.assertFalse(self.h.verify_ledger())

    def test_repeated_transition_validly_hashed_is_not_certified(self):
        task = self.h.submit(spec(), idempotency_key="duplicate-transition")
        self.h.prepare(task)
        with self.h._conn() as conn:
            conn.execute("BEGIN IMMEDIATE")
            self.h._event(conn, task, "PREPARED", {"state": "READY"})
        self.assertFalse(self.h.verify_ledger())

    def test_untampered_high_risk_terminal_states_and_recovery(self):
        approved = self.h.submit(spec("demo.review"), idempotency_key="approved")
        self.h.prepare(approved)
        token = self.issuer.issue(task_id=approved, spec_hash=self.h.task(approved)["spec_hash"],
                                  approver="synthetic-only", decision="approve")
        self.h.approve(approved, token)
        self.h.execute_demo(approved)
        denied = self.h.submit(spec("demo.review"), idempotency_key="denied")
        self.h.prepare(denied)
        token = self.issuer.issue(task_id=denied, spec_hash=self.h.task(denied)["spec_hash"],
                                  approver="synthetic-only", decision="reject")
        self.h.approve(denied, token)
        running = self.h.submit(spec(), idempotency_key="running")
        self.h.prepare(running)
        self.h.reserve(running)
        self.h.recover_interrupted()
        self.assertTrue(self.h.verify_ledger())


class DecisionBoundaryTests(unittest.TestCase):
    setUp = DurableStateLedgerTests.setUp
    tamper = DurableStateLedgerTests.tamper

    def test_low_risk_forged_ready_does_not_reserve(self):
        task = self.h.submit(spec(), idempotency_key="skip-prepare")
        self.tamper("UPDATE tasks SET state='READY' WHERE task_id=?", (task,))
        with self.assertRaises(GateError):
            self.h.reserve(task)

    def test_corrupt_state_does_not_forge_successful_read(self):
        task = self.h.submit(spec(), idempotency_key="fake-result")
        self.tamper("UPDATE tasks SET state='SUCCEEDED',result=? WHERE task_id=?",
                    (json.dumps({"action": "demo.echo", "external_effects": False, "preview": "fake"}), task))
        with self.assertRaises(GateError):
            self.h.execute_demo(task)


if __name__ == "__main__":
    unittest.main()
