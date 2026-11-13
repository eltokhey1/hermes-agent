"""Research-only: independent monotonic floor and nonproduction P0/P1 probes.

A test-maintained epoch represents what a trusted external watchdog WOULD have
to remember; no real secure counter, user identity, protected file or external
action is present. This is not owner-machine acceptance.
"""
from __future__ import annotations

from contextlib import closing
import json
import secrets
import shutil
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from isolated_authority_research import _Boundary
from orchestrator import GateError


def spec():
    return {"action": "demo.review", "input": "synthetic preview only",
            "estimated_cost_usd": 0, "network_allowed": False,
            "target_environment": "sandbox"}


class IndependentEpochRollbackResearch(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.db = self.root / "lab.sqlite"
        self.anchor = self.root / "anchor.json"
        self.snapdb = self.root / "snapshot.sqlite"
        self.key = secrets.token_bytes(32)
        self.h = _Boundary(self.db, checkpoint_path=self.anchor,
                           signing_key=self.key, bootstrap=True)

    def submit(self):
        result = self.h.agent({"op": "submit", "spec": spec(),
                               "idempotency_key": secrets.token_hex(16)})
        self.assertEqual(result["state"], "WAITING_APPROVAL")
        return result

    def backup_snapshot(self):
        # SQLite online backup API, never raw-copy live DB or delete WAL.
        with closing(sqlite3.connect(self.db)) as source:
            with closing(sqlite3.connect(self.snapdb)) as target:
                source.backup(target)
                self.assertEqual(target.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        receipt_bytes = self.anchor.read_bytes()
        return receipt_bytes, json.loads(receipt_bytes)["epoch"]

    def rewind_both(self, receipt_bytes):
        # In a synthetic adversarial test only: rewrite BOTH database & receipt.
        with closing(sqlite3.connect(self.snapdb)) as old:
            with closing(sqlite3.connect(self.db)) as destination:
                old.backup(destination)
        self.anchor.write_bytes(receipt_bytes)

    def test_synthetic_p0_isolated_restore_does_not_mutate_original(self):
        task = self.submit()
        receipt_bytes, epoch = self.backup_snapshot()
        target_dir = self.root / "disposable-restore"
        target_dir.mkdir()
        target_db = target_dir / "restored.sqlite"
        target_receipt = target_dir / "receipt.json"
        with closing(sqlite3.connect(self.snapdb)) as old:
            with closing(sqlite3.connect(target_db)) as restored:
                old.backup(restored)
                self.assertEqual(restored.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        target_receipt.write_bytes(receipt_bytes)
        isolated = _Boundary(target_db, checkpoint_path=target_receipt,
                             signing_key=self.key, minimum_expected_epoch=epoch)
        self.assertEqual(isolated.agent({"op": "status", "task_id": task["task_id"]})["state"],
                         "WAITING_APPROVAL")
        self.assertEqual(self.h.agent({"op": "status", "task_id": task["task_id"]})["state"],
                         "WAITING_APPROVAL")

    def test_current_design_without_external_floor_accepts_full_rollback_gap(self):
        self.submit()
        old_receipt, old_epoch = self.backup_snapshot()
        second = self.submit()
        latest_epoch = json.loads(self.anchor.read_text("utf-8"))["epoch"]
        self.assertGreater(latest_epoch, old_epoch)
        self.rewind_both(old_receipt)
        # This is intentionally a PASS that documents a real gap (not a fix).
        unprotected = _Boundary(self.db, checkpoint_path=self.anchor,
                                signing_key=self.key, bootstrap=False)
        self.assertEqual(unprotected.agent({"op": "pid"})["preview_only"], True)
        with self.assertRaises(GateError):
            unprotected.agent({"op": "status", "task_id": second["task_id"]})

    def test_independently_retained_epoch_floor_detects_full_rollback(self):
        self.submit()
        old_receipt, old_epoch = self.backup_snapshot()
        self.submit()
        trusted_epoch_held_outside_both_files = json.loads(
            self.anchor.read_text("utf-8"))["epoch"]
        self.assertGreater(trusted_epoch_held_outside_both_files, old_epoch)
        self.rewind_both(old_receipt)
        with self.assertRaisesRegex(GateError, "ANCHOR_ROLLBACK_DETECTED"):
            _Boundary(self.db, checkpoint_path=self.anchor, signing_key=self.key,
                      minimum_expected_epoch=trusted_epoch_held_outside_both_files)

    def test_external_epoch_floor_prevents_estop_downgrade_by_full_rollback(self):
        task = self.submit()
        receipt_before_estop, old_epoch = self.backup_snapshot()
        result = self.h.owner({"op": "estop"}, threading.Event())
        self.assertTrue(result["estop_latched"])
        trusted_epoch = json.loads(self.anchor.read_text("utf-8"))["epoch"]
        self.assertGreater(trusted_epoch, old_epoch)
        self.rewind_both(receipt_before_estop)
        with self.assertRaisesRegex(GateError, "ANCHOR_ROLLBACK_DETECTED"):
            _Boundary(self.db, checkpoint_path=self.anchor, signing_key=self.key,
                      minimum_expected_epoch=trusted_epoch)
        # Without the protected epoch, a stale signed checkpoint can clear ESTOP:
        vulnerable = _Boundary(self.db, checkpoint_path=self.anchor, signing_key=self.key)
        self.assertFalse(vulnerable.estop)  # evidence of the remaining hard requirement

    def test_interrupted_db_commit_before_anchor_advance_is_fail_closed(self):
        self.submit()
        # Simulates the crash window: DB has committed but durable anchor was
        # not advanced. No actual external tool was ever invoked.
        self.h.core.submit(spec(), idempotency_key="simulated-crash-after-db-commit")
        with self.assertRaisesRegex(GateError, "EXTERNAL_ANCHOR_MISMATCH"):
            _Boundary(self.db, checkpoint_path=self.anchor, signing_key=self.key)

    def test_reject_model_supplied_epoch_floor_types(self):
        for bad in (True, False, 0, -1, "2", 2.5):
            with self.subTest(bad=bad), self.assertRaisesRegex(
                GateError, "TRUSTED_EPOCH_REQUIRED"
            ):
                _Boundary(self.db, checkpoint_path=self.anchor,
                          signing_key=self.key, minimum_expected_epoch=bad)

    def test_identity_not_granted_by_authenticated_test_channel(self):
        # This synthetic harness proves no human identity; it must never
        # generate an authenticated-user verdict from a simple channel token.
        self.assertNotIn("human_authentication", self.h.agent({"op": "pid"}))
        self.assertFalse(self.h.agent({"op": "pid"}).get("production_ready", False))


if __name__ == "__main__":
    unittest.main()
