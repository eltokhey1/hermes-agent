"""Metrics must not conceal corrupted durable task state."""
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from approvals import ApprovalVerifier
from orchestrator import GateError, HermesReference
from test_secure_orchestrator import Clock, spec

class ObservabilityIntegrityTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "state.sqlite"
        self.h = HermesReference(self.path, verifier=ApprovalVerifier(
            b"synthetic-only-approval-test-key-32bytes", clock=Clock()))

    def test_valid_snapshot_remains_available(self):
        self.h.submit(spec(), idempotency_key="healthy")
        self.assertEqual(self.h.status_summary()["tasks_by_state"], {"PENDING": 1})

    def test_forged_succeeded_cannot_be_reported_as_health(self):
        task = self.h.submit(spec(), idempotency_key="forged-success")
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE tasks SET state='SUCCEEDED' WHERE task_id=?", (task,))
        with self.assertRaises(GateError):
            self.h.status_summary()

    def test_valid_prefix_with_deleted_event_cannot_be_reported_as_health(self):
        task = self.h.submit(spec(), idempotency_key="removed-event")
        self.h.prepare(task)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("DELETE FROM events WHERE event_type='PREPARED' AND task_id=?", (task,))
        with self.assertRaises(GateError):
            self.h.status_summary()

if __name__ == "__main__":
    unittest.main()
