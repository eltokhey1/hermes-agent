"""Synthetic P0/P1 research: durable authority checkpoint across process restart.

This is not a protected machine trust root: all tests use the runner's single
OS identity and synthetic secret. The two IPC authentication tokens are
independent of the synthetic approval signing secret.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import secrets
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from isolated_authority_research import _Boundary, exchange, serve_authority
from orchestrator import GateError


def harmless_spec():
    return {"action": "demo.review", "input": "no external effect",
            "estimated_cost_usd": 0, "network_allowed": False,
            "target_environment": "sandbox"}


class DurableRestartResearch(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.db = self.root / "state.sqlite"
        self.checkpoint = self.root / "separate-research-checkpoint.json"
        self.signing_key = secrets.token_bytes(32)
        self.agent_key = secrets.token_bytes(32)
        self.owner_key = secrets.token_bytes(32)
        self.proc = None
        self.addCleanup(self.stop)

    def start(self, *, bootstrap=False):
        ctx = mp.get_context("spawn")
        ready = ctx.Queue()
        self.proc = ctx.Process(
            target=serve_authority,
            args=(str(self.db), self.agent_key, self.owner_key, ready,
                  str(self.checkpoint), self.signing_key, bootstrap),
            daemon=True,
        )
        self.proc.start()
        self.endpoint = ready.get(timeout=20)
        self.assertTrue(self.proc.is_alive())
        self.assertEqual(self.proc.pid, self.endpoint["pid"])

    def stop(self):
        if self.proc is not None:
            if self.proc.is_alive():
                self.proc.terminate()
            self.proc.join(timeout=10)
            if self.proc.is_alive():
                self.proc.kill()
                self.proc.join(timeout=10)
            self.proc = None

    def agent(self, **req):
        return exchange(self.endpoint["agent_address"], self.agent_key, req)

    def owner(self, **req):
        return exchange(self.endpoint["owner_address"], self.owner_key, req)

    def propose(self):
        result = self.agent(op="submit", spec=harmless_spec(),
                            idempotency_key=secrets.token_hex(16))
        self.assertTrue(result["ok"], result)
        return result["data"]

    def approve(self, task):
        result = self.owner(op="decision", task_id=task["task_id"],
                            spec_hash=task["spec_hash"], decision="approve")
        self.assertTrue(result["ok"], result)

    def test_fresh_boot_requires_explicit_bootstrap(self):
        with self.assertRaisesRegex(GateError, "ANCHOR_MISSING"):
            _Boundary(self.db, checkpoint_path=self.checkpoint,
                      signing_key=self.signing_key, bootstrap=False)
        self.assertFalse(self.checkpoint.exists())

    def test_approval_remains_bound_after_authority_process_restart(self):
        self.start(bootstrap=True)
        task = self.propose()
        self.approve(task)
        saved = json.loads(self.checkpoint.read_text("utf-8"))
        self.assertGreaterEqual(saved["epoch"], 2)
        first_pid = self.proc.pid
        self.stop()
        self.start(bootstrap=False)
        self.assertNotEqual(self.proc.pid, first_pid)
        state = self.agent(op="status", task_id=task["task_id"])
        self.assertEqual(state["data"]["state"], "READY")
        wrong_hash = self.agent(op="dispatch", task_id=task["task_id"],
                                spec_hash="0" * 64)
        self.assertFalse(wrong_hash["ok"])
        ok = self.agent(op="dispatch", task_id=task["task_id"],
                        spec_hash=task["spec_hash"])
        self.assertTrue(ok["ok"], ok)
        self.assertFalse(ok["data"]["result"]["external_effects"])

    def test_estop_latch_survives_authority_crash_and_restart(self):
        self.start(bootstrap=True)
        task = self.propose()
        self.approve(task)
        self.assertTrue(self.owner(op="estop")["data"]["estop_latched"])
        self.stop()
        self.start(bootstrap=False)
        denied = self.agent(op="dispatch", task_id=task["task_id"],
                            spec_hash=task["spec_hash"])
        self.assertFalse(denied["ok"])
        self.assertIn("ESTOP_LATCHED", denied["error"])

    def test_changed_checkpoint_mac_is_denied_while_server_runs(self):
        self.start(bootstrap=True)
        task = self.propose()
        document = json.loads(self.checkpoint.read_text("utf-8"))
        document["mac"] = "0" * 64
        self.checkpoint.write_text(json.dumps(document), encoding="utf-8")
        denied = self.agent(op="status", task_id=task["task_id"])
        self.assertFalse(denied["ok"])
        self.assertIn("ANCHOR_SIGNATURE_MISMATCH", denied["error"])

    def test_deleted_checkpoint_not_rebootstrapped_with_existing_evidence(self):
        self.start(bootstrap=True)
        self.propose()
        self.stop()
        self.checkpoint.unlink()
        with self.assertRaisesRegex(GateError, "BOOTSTRAP_REQUIRES_EMPTY_LEDGER"):
            _Boundary(self.db, checkpoint_path=self.checkpoint,
                      signing_key=self.signing_key, bootstrap=True)

    def test_sqlite_rewrite_with_original_checkpoint_refused_on_reboot(self):
        self.start(bootstrap=True)
        task = self.propose()
        self.stop()
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute("DELETE FROM events WHERE task_id=?", (task["task_id"],))
            conn.commit()
        with self.assertRaisesRegex(GateError, "EXTERNAL_ANCHOR_MISMATCH"):
            _Boundary(self.db, checkpoint_path=self.checkpoint,
                      signing_key=self.signing_key, bootstrap=False)

    def test_wrong_persisted_authority_key_denied(self):
        self.start(bootstrap=True)
        self.stop()
        with self.assertRaisesRegex(GateError, "ANCHOR_SIGNATURE_MISMATCH"):
            _Boundary(self.db, checkpoint_path=self.checkpoint,
                      signing_key=secrets.token_bytes(32), bootstrap=False)


if __name__ == "__main__":
    unittest.main()
