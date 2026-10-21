"""Negative regression checks against stale/tampered durable state."""
from contextlib import closing
import sqlite3
import unittest

from test_secure_orchestrator import Clock, spec
from approvals import ApprovalIssuer, ApprovalVerifier
from orchestrator import HermesReference
import tempfile
from pathlib import Path
from orchestrator import GateError


class PersistenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "reference.sqlite"
        self.clock = Clock()
        key = b"synthetic-only-approval-test-key-32bytes"
        self.issuer = ApprovalIssuer(key, clock=self.clock)
        self.verifier = ApprovalVerifier(key, clock=self.clock)
        self.h = HermesReference(self.path, verifier=self.verifier)

    def add(self, action="demo.echo", key="a"):
        task = self.h.submit(spec(action), idempotency_key=key)
        self.h.prepare(task)
        return task

    def token(self, task):
        return self.issuer.issue(task_id=task, spec_hash=self.h.task(task)["spec_hash"],
                                 approver="test-human-not-authenticated", decision="approve")

    def test_tampered_spec_before_prepare_fails_closed(self):
        task = self.h.submit(spec(), idempotency_key="spec-before-prepare")
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE tasks SET spec=? WHERE task_id=?", (self.h_spec_high(), task))
        with self.assertRaises(GateError):
            self.h.prepare(task)

    def test_tampered_spec_after_approval_fails_closed(self):
        task = self.add("demo.review", "spec-after-approval")
        self.h.approve(task, self.token(task))
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE tasks SET spec=? WHERE task_id=?", (self.h_spec_low(), task))
        with self.assertRaises(GateError):
            self.h.reserve(task)

    def h_spec_low(self):
        import json
        return json.dumps(spec(), sort_keys=True)

    def h_spec_high(self):
        import json
        return json.dumps(spec("demo.review"), sort_keys=True)

    def test_tampered_spec_prevents_idempotent_retrieval(self):
        task = self.h.submit(spec(), idempotency_key="spec-on-retry")
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE tasks SET spec='{}' WHERE task_id=?", (task,))
        with self.assertRaises(GateError):
            self.h.submit(spec(), idempotency_key="spec-on-retry")

    def test_tampered_spec_prevents_read(self):
        task = self.h.submit(spec(), idempotency_key="spec-read")
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE tasks SET spec=? WHERE task_id=?", (self.h_spec_high(), task))
        with self.assertRaises(GateError):
            self.h.task(task)

    def test_missing_event_chain_with_tasks_is_invalid(self):
        self.h.submit(spec(), idempotency_key="truncated-ledger")
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("DELETE FROM events")
        self.assertFalse(self.h.verify_ledger())

    def test_tampered_spec_prevents_finish(self):
        task = self.add(key="spec-running")
        self.h.reserve(task)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE tasks SET spec=? WHERE task_id=?", (self.h_spec_high(), task))
        with self.assertRaises(GateError):
            self.h.finish_demo(task)
