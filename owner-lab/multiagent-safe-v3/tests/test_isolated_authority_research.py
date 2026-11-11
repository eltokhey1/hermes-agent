"""Adversarial process-boundary smoke, stdlib only, entirely synthetic.

These tests simulate separated credentials, NOT operating-system ACL isolation.
Uses spawn on Windows and Linux so the authority is a different OS process.
"""
from __future__ import annotations

import concurrent.futures
import multiprocessing as mp
import os
import secrets
import sqlite3
import tempfile
import time
import unittest
from multiprocessing.connection import AuthenticationError
from pathlib import Path

from isolated_authority_research import exchange, serve_authority


def spec(action="demo.review", **overrides):
    body = {"action": action, "input": "inert synthetic preview",
            "estimated_cost_usd": 0, "network_allowed": False,
            "target_environment": "sandbox"}
    body.update(overrides)
    return body


class IsolatedAuthorityResearch(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        ctx = mp.get_context("spawn")
        self.agent_auth = secrets.token_bytes(32)
        self.owner_auth = secrets.token_bytes(32)
        ready = ctx.Queue()
        self.proc = ctx.Process(
            target=serve_authority,
            args=(str(Path(self.tempdir.name) / "lab.sqlite"),
                  self.agent_auth, self.owner_auth, ready),
            daemon=True,
        )
        self.proc.start()
        self.addCleanup(self._stop)
        self.endpoint = ready.get(timeout=20)
        self.assertEqual(self.proc.pid, self.endpoint["pid"])

    def _stop(self):
        if self.proc.is_alive():
            self.proc.terminate()
        self.proc.join(timeout=8)
        if self.proc.is_alive():
            self.proc.kill()
            self.proc.join(timeout=8)

    def agent(self, **command):
        return exchange(self.endpoint["agent_address"], self.agent_auth, command)

    def owner(self, **command):
        return exchange(self.endpoint["owner_address"], self.owner_auth, command)

    def proposal(self, action="demo.review"):
        result = self.agent(op="submit", spec=spec(action), idempotency_key=secrets.token_hex(16))
        self.assertTrue(result["ok"], result)
        return result["data"]

    def approval(self, item, decision="approve", ttl_seconds=180):
        return self.owner(op="decision", task_id=item["task_id"],
                          spec_hash=item["spec_hash"], decision=decision,
                          ttl_seconds=ttl_seconds)

    def test_authority_is_an_independent_os_process(self):
        who = self.agent(op="pid")
        self.assertTrue(who["ok"])
        self.assertNotEqual(os.getpid(), who["data"]["pid"])
        self.assertTrue(who["data"]["preview_only"])

    def test_agent_approval_operation_is_not_exposed(self):
        pending = self.proposal()
        deny = self.agent(op="decision", decision="approve", task_id=pending["task_id"],
                          spec_hash=pending["spec_hash"])
        self.assertFalse(deny["ok"])
        self.assertIn("AGENT_OPERATION_DENIED", deny["error"])
        self.assertEqual("WAITING_APPROVAL", self.agent(op="status",
                         task_id=pending["task_id"])["data"]["state"])

    def test_agent_capability_cannot_authenticate_to_owner_channel(self):
        with self.assertRaises(AuthenticationError):
            exchange(self.endpoint["owner_address"], self.agent_auth,
                     {"op": "decision", "task_id": "x", "decision": "approve"})
        self.assertTrue(self.proc.is_alive())

    def test_high_risk_requires_owner_decision_and_exact_hash(self):
        pending = self.proposal()
        before = self.agent(op="dispatch", task_id=pending["task_id"],
                            spec_hash=pending["spec_hash"])
        self.assertFalse(before["ok"])
        mismatch = self.owner(op="decision", task_id=pending["task_id"],
                              spec_hash="0" * 64, decision="approve")
        self.assertFalse(mismatch["ok"])
        self.assertIn("EXACT_ACTION_HASH_MISMATCH", mismatch["error"])
        self.assertTrue(self.approval(pending)["ok"])
        wrong = self.agent(op="dispatch", task_id=pending["task_id"], spec_hash="f" * 64)
        self.assertFalse(wrong["ok"])
        self.assertIn("EXACT_ACTION_HASH_MISMATCH", wrong["error"])
        good = self.agent(op="dispatch", task_id=pending["task_id"],
                          spec_hash=pending["spec_hash"])
        self.assertTrue(good["ok"], good)
        self.assertEqual(good["data"]["state"], "SUCCEEDED")
        self.assertFalse(good["data"]["result"]["external_effects"])

    def test_reject_decision_cannot_authorize(self):
        pending = self.proposal()
        result = self.approval(pending, decision="reject")
        self.assertTrue(result["ok"])
        self.assertEqual(result["data"]["state"], "REJECTED")
        blocked = self.agent(op="dispatch", task_id=pending["task_id"],
                             spec_hash=pending["spec_hash"])
        self.assertFalse(blocked["ok"])

    def test_expired_decision_rejected_at_dispatch(self):
        pending = self.proposal()
        self.assertTrue(self.approval(pending, ttl_seconds=1)["ok"])
        time.sleep(1.25)
        expired = self.agent(op="dispatch", task_id=pending["task_id"],
                             spec_hash=pending["spec_hash"])
        self.assertFalse(expired["ok"])
        self.assertIn("expired", expired["error"].lower())
        self.assertEqual(self.agent(op="status", task_id=pending["task_id"])["data"]["state"], "READY")

    def test_simulated_estop_latch_denies_dispatch(self):
        pending = self.proposal()
        self.assertTrue(self.approval(pending)["ok"])
        stop = self.owner(op="estop")
        self.assertTrue(stop["ok"])
        self.assertTrue(stop["data"]["estop_latched"])
        denied = self.agent(op="dispatch", task_id=pending["task_id"],
                            spec_hash=pending["spec_hash"])
        self.assertFalse(denied["ok"])
        self.assertIn("ESTOP_LATCHED", denied["error"])

    def test_untrusted_model_cannot_supply_risk_or_paid_action(self):
        injected = self.agent(op="submit", spec=spec("demo.review", risk="low"),
                              idempotency_key="fake-risk")
        self.assertFalse(injected["ok"])
        paid = self.agent(op="submit", spec=spec("demo.review", estimated_cost_usd=1),
                          idempotency_key="paid")
        self.assertFalse(paid["ok"])
        send = self.agent(op="submit", spec=spec("payment.send"), idempotency_key="payment")
        self.assertFalse(send["ok"])
        self.assertTrue(self.proc.is_alive())

    def test_same_action_hash_repeated_dispatch_is_inert_and_idempotent(self):
        pending = self.proposal()
        self.assertTrue(self.approval(pending)["ok"])
        def call():
            return self.agent(op="dispatch", task_id=pending["task_id"], spec_hash=pending["spec_hash"])
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(lambda _: call(), range(2)))
        self.assertTrue(all(r["ok"] for r in replies), replies)
        self.assertEqual(replies[0]["data"]["result"], replies[1]["data"]["result"])
        self.assertTrue(all(r["data"]["result"]["external_effects"] is False for r in replies))
        with sqlite3.connect(Path(self.tempdir.name) / "lab.sqlite") as conn:
            count = conn.execute("SELECT count(*) FROM events WHERE event_type='STARTED'").fetchone()[0]
        self.assertEqual(count, 1)

    def test_out_of_band_ledger_edit_denied_against_separate_process_memory_anchor(self):
        pending = self.proposal()
        with sqlite3.connect(Path(self.tempdir.name) / "lab.sqlite") as conn:
            conn.execute("DELETE FROM events WHERE task_id=?", (pending["task_id"],))
            conn.commit()
        check = self.agent(op="status", task_id=pending["task_id"])
        self.assertFalse(check["ok"])
        self.assertIn("EXTERNAL_ANCHOR_MISMATCH", check["error"])


if __name__ == "__main__":
    unittest.main()
