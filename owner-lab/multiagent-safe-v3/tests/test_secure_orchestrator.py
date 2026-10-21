"""Synthetic, no I/O outside isolated temporary SQLite; NOT production acceptance."""
import concurrent.futures
from contextlib import closing
import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from approvals import ApprovalIssuer, ApprovalVerifier, ApprovalDenied
from orchestrator import HermesReference, GateError, digest


class Clock:
    def __init__(self):
        self.t = 1_800_000_000

    def __call__(self):
        return self.t


def spec(action="demo.echo", **updates):
    data = {"action": action, "input": "inert preview", "estimated_cost_usd": 0,
            "network_allowed": False, "target_environment": "sandbox"}
    data.update(updates)
    return data


class SecureOrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "reference.sqlite"
        self.clock = Clock()
        self.key = b"synthetic-only-approval-test-key-32bytes"
        self.issuer = ApprovalIssuer(self.key, clock=self.clock)
        self.verifier = ApprovalVerifier(self.key, clock=self.clock)
        self.h = HermesReference(self.path, verifier=self.verifier)

    def add(self, action="demo.echo", key="a"):
        task = self.h.submit(spec(action), idempotency_key=key)
        self.h.prepare(task)
        return task

    def token(self, task, *, decision="approve", authority=None, ttl=180, spec_hash=None):
        return (authority or self.issuer).issue(task_id=task,
                spec_hash=spec_hash or self.h.task(task)["spec_hash"],
                approver="lab-human-test", decision=decision, ttl_seconds=ttl)

    def test_low_risk_preview_is_inert(self):
        task = self.add()
        self.assertEqual("READY", self.h.task(task)["state"])
        result = self.h.execute_demo(task)
        self.assertFalse(result["external_effects"])
        self.assertEqual("SUCCEEDED", self.h.task(task)["state"])
        self.assertEqual(result, self.h.execute_demo(task))

    def test_high_risk_requires_approval(self):
        task = self.add("demo.review")
        self.assertEqual("WAITING_APPROVAL", self.h.task(task)["state"])
        with self.assertRaises(GateError):
            self.h.execute_demo(task)
        self.assertEqual("READY", self.h.approve(task, self.token(task)))
        self.assertEqual("SUCCEEDED", self.h.execute_demo(task) and self.h.task(task)["state"])

    def test_model_supplied_risk_and_privileges_rejected(self):
        for data in ({"risk": "low"}, {"actor": "owner"}, {"allow_unsafe": True}):
            with self.subTest(data=data), self.assertRaises(GateError):
                self.h.submit(spec(**data), idempotency_key="bad" + str(len(data)))

    def test_unknown_action_and_external_effects_denied(self):
        for action in ("deploy", "payment.send", "ros2.publish", "demo.echo; curl evil"):
            with self.subTest(action=action), self.assertRaises(GateError):
                self.h.submit(spec(action), idempotency_key=action)
        for change in ({"estimated_cost_usd": 1}, {"network_allowed": True},
                       {"target_environment": "production"}, {"estimated_cost_usd": True},
                       {"estimated_cost_usd": float("nan")}):
            with self.subTest(change=change), self.assertRaises(GateError):
                self.h.submit(spec(**change), idempotency_key="denied")

    def test_conflicting_idempotency_key_rejected(self):
        first = self.h.submit(spec(), idempotency_key="collision")
        self.assertEqual(first, self.h.submit(spec(), idempotency_key="collision"))
        with self.assertRaises(GateError):
            self.h.submit(spec(input="changed"), idempotency_key="collision")

    def test_hmac_tampering_rejected(self):
        task = self.add("demo.review")
        token = self.token(task)
        header, sig = token.split(".")
        altered = header + "." + ("A" if sig[0] != "A" else "B") + sig[1:]
        with self.assertRaises(GateError):
            self.h.approve(task, altered)
        self.assertEqual("WAITING_APPROVAL", self.h.task(task)["state"])

    def test_wrong_key_rejected(self):
        task = self.add("demo.review")
        other = ApprovalIssuer(b"different-synthetic-approval-test-key!", clock=self.clock)
        with self.assertRaises(GateError):
            self.h.approve(task, self.token(task, authority=other))

    def test_expired_approval_rejected_at_acceptance(self):
        task = self.add("demo.review")
        token = self.token(task, ttl=4)
        self.clock.t += 4
        with self.assertRaises(GateError):
            self.h.approve(task, token)

    def test_approved_but_expired_before_execution_denied(self):
        task = self.add("demo.review")
        self.h.approve(task, self.token(task, ttl=3))
        self.clock.t += 3
        with self.assertRaises(GateError):
            self.h.execute_demo(task)
        self.assertEqual("READY", self.h.task(task)["state"])

    def test_future_dated_assertion_denied(self):
        task = self.add("demo.review")
        token = self.token(task)
        self.clock.t -= 10
        with self.assertRaises(GateError):
            self.h.approve(task, token)

    def test_rejected_never_executes(self):
        task = self.add("demo.review")
        self.assertEqual("REJECTED", self.h.approve(task, self.token(task, decision="reject")))
        with self.assertRaises(GateError):
            self.h.execute_demo(task)
        with self.assertRaises(GateError):
            self.h.approve(task, self.token(task))

    def test_wrong_task_token_rejected(self):
        first = self.add("demo.review", "one")
        second = self.add("demo.review", "two")
        with self.assertRaises(GateError):
            self.h.approve(second, self.token(first))
        self.assertEqual("WAITING_APPROVAL", self.h.task(second)["state"])

    def test_wrong_spec_hash_rejected(self):
        task = self.add("demo.review")
        with self.assertRaises(GateError):
            self.h.approve(task, self.token(task, spec_hash="0"*64))

    def test_replay_denied(self):
        task = self.add("demo.review")
        token = self.token(task)
        self.h.approve(task, token)
        with self.assertRaises(GateError):
            self.h.approve(task, token)
        self.assertEqual("READY", self.h.task(task)["state"])

    def test_token_not_exposed_in_task_or_ledger(self):
        task = self.add("demo.review")
        token = self.token(task)
        self.h.approve(task, token)
        self.assertNotIn(token, str(self.h.task(task)))
        with closing(sqlite3.connect(self.path)) as db, db:
            log = repr(db.execute("SELECT payload FROM events").fetchall())
        self.assertNotIn(token, log)

    def test_token_not_approved_by_just_name(self):
        task = self.add("demo.review")
        with self.assertRaises(GateError):
            self.h.approve(task, "lab-human-test")

    def test_ttl_bounds(self):
        task = self.add("demo.review")
        for t in (0, 601, 1.2, True):
            with self.subTest(t=t), self.assertRaises(ApprovalDenied):
                self.token(task, ttl=t)

    def test_verifier_cannot_issue_assertions(self):
        self.assertFalse(hasattr(self.h.verifier, "issue"))

    def test_requires_verifier_and_strong_key(self):
        with self.assertRaises(GateError):
            HermesReference(self.path, verifier=None)
        with self.assertRaises(ApprovalDenied):
            ApprovalVerifier(b"short", clock=self.clock)

    def test_ready_state_survives_restart_with_verifier(self):
        task = self.add("demo.review")
        self.h.approve(task, self.token(task))
        restarted = HermesReference(self.path, verifier=self.verifier)
        self.assertEqual("SUCCEEDED", restarted.execute_demo(task) and restarted.task(task)["state"])

    def test_running_after_crash_marked_unknown(self):
        task = self.add()
        self.h.reserve(task)  # crash here, before any effect
        restarted = HermesReference(self.path, verifier=self.verifier)
        self.assertEqual(1, restarted.recover_interrupted())
        self.assertEqual("UNKNOWN", restarted.task(task)["state"])
        self.assertEqual(0, restarted.recover_interrupted())
        with self.assertRaises(GateError):
            restarted.execute_demo(task)

    def test_high_risk_crash_no_replay(self):
        task = self.add("demo.review")
        self.h.approve(task, self.token(task))
        self.h.reserve(task)
        self.assertEqual(1, HermesReference(self.path, verifier=self.verifier).recover_interrupted())
        with self.assertRaises(GateError):
            self.h.execute_demo(task)

    def test_ledger_tamper_detection(self):
        task = self.add()
        self.h.execute_demo(task)
        self.assertTrue(self.h.verify_ledger())
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE events SET event_type='FORGED' WHERE seq=1")
        self.assertFalse(self.h.verify_ledger())

    def test_ledger_corrupt_json_is_false(self):
        task = self.add()
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE events SET payload='not json' WHERE seq=1")
        self.assertFalse(self.h.verify_ledger())

    def test_parallel_same_idempotency_key_stable(self):
        def job(_):
            other = HermesReference(self.path, verifier=self.verifier)
            return other.submit(spec(), idempotency_key="parallel")
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(job, range(12)))
        self.assertEqual(1, len(set(results)))
        with closing(sqlite3.connect(self.path)) as db, db:
            self.assertEqual(1, db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0])

    def test_parallel_reserve_one_winner(self):
        task = self.add()
        def reserve(_):
            try:
                self.h.reserve(task)
                return True
            except GateError:
                return False
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            outcomes = list(pool.map(reserve, range(4)))
        self.assertEqual(1, outcomes.count(True))
        self.assertEqual("RUNNING", self.h.task(task)["state"])

    def test_redacted_observability_snapshot(self):
        task = self.add()
        snapshot = self.h.status_summary()
        self.assertEqual(snapshot["tasks_by_state"], {"READY": 1})
        self.assertEqual(snapshot["last_event_seq"], 2)
        self.assertFalse(snapshot["external_effects_enabled"])
        self.assertEqual(snapshot["model_api_cost_usd"], 0)
        self.assertNotIn("inert preview", repr(snapshot))

    def test_ledger_preserves_hash_chain_after_recovery(self):
        task = self.add()
        self.h.reserve(task)
        self.h.recover_interrupted()
        self.assertTrue(self.h.verify_ledger())


if __name__ == '__main__':
    unittest.main()
