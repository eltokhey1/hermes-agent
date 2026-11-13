from __future__ import annotations

from contextlib import closing
import json
import multiprocessing as mp
from multiprocessing.connection import AuthenticationError
from pathlib import Path
import secrets
import shutil
import sqlite3
import tempfile
import time
import unittest

from authority import (Denied, OwnerAuthorityResearch, ProtectedRootResearch,
                       SyntheticProofVerifier, action_hash, sha256)
from ipc_service import root_process, authority_process, request
from test_identity_research import SyntheticIssuer


def action(task=None, **updates):
    spec = {"task_id": task or secrets.token_hex(16), "effect": "demo.review",
            "target": "synthetic-only", "input_sha256": sha256(b"no real data"),
            "cost_usd": 0, "environment": "sandbox"}
    spec.update(updates)
    return spec


class Clock:
    def __init__(self):
        self.t = 1800000000
    def __call__(self):
        return self.t


class CoreSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.clock = Clock()
        self.keys = [secrets.token_bytes(32) for _ in range(3)]
        self.root = ProtectedRootResearch(self.folder / "external-root.sqlite", self.keys[0])
        self.issuer = SyntheticIssuer(self.keys[1], self.clock)
        self.verifier = SyntheticProofVerifier(self.keys[1],
                                                subject="synthetic-owner", clock=self.clock)
        self.db = self.folder / "authority.sqlite"
        self.authority = OwnerAuthorityResearch(self.db, self.root, self.verifier,
                                                 self.keys[2], bootstrap=True,
                                                 clock=self.clock)

    def owner(self, subject="synthetic-owner", session=None, ttl=120):
        return self.issuer.mint(subject, session=session, ttl_seconds=ttl)

    def pending(self):
        contract = action()
        proposed = self.authority.submit(contract)
        return contract, proposed

    def approve(self, contract=None, *, token=None, challenge=None, csrf=None,
                decision="approve", exact_hash=None):
        if contract is None:
            contract, _ = self.pending()
        identity = token or self.owner()
        if challenge is None:
            challenge = self.authority.begin_review(contract["task_id"], identity)["review_challenge"]
        verdict = self.authority.decide(
            task_id=contract["task_id"], expected_hash=exact_hash or action_hash(contract),
            decision=decision, synthetic_identity_proof=identity,
            csrf_challenge=challenge, csrf_echo=csrf if csrf is not None else challenge,
        )
        return contract, verdict

    def test_exact_action_approved_once_only_and_inert(self):
        contract, result = self.approve()
        self.assertEqual(result["state"], "APPROVED")
        preview = self.authority.preview(contract["task_id"], action_hash(contract))
        self.assertEqual(preview["result"], "INERT_PREVIEW")
        self.assertFalse(preview["external_effects"])
        with self.assertRaisesRegex(Denied, "NOT_APPROVED_OR_REPLAYED"):
            self.authority.preview(contract["task_id"], action_hash(contract))

    def test_agent_supplied_effect_and_paid_cost_denied(self):
        for invalid in (action(effect="payment.send"), action(cost_usd=1),
                        action(cost_usd=True), action(environment="production"),
                        action(target="real-provider"), action(effect="demo.review", risk="low")):
            with self.subTest(invalid=invalid), self.assertRaises(Denied):
                self.authority.submit(invalid)

    def test_wrong_action_hash_does_not_consume_grant(self):
        contract, _ = self.approve()
        with self.assertRaisesRegex(Denied, "EXACT_ACTION_HASH_MISMATCH"):
            self.authority.preview(contract["task_id"], "0" * 64)
        self.assertEqual(self.authority.preview(contract["task_id"], action_hash(contract))["result"],
                         "INERT_PREVIEW")

    def test_forged_owner_signature_and_subject_rejected(self):
        c, _ = self.pending()
        with self.assertRaisesRegex(Denied, "INVALID_SIGNATURE"):
            self.authority.begin_review(c["task_id"], SyntheticIssuer(secrets.token_bytes(32), self.clock).mint())
        with self.assertRaisesRegex(Denied, "OWNER_IDENTITY_PROOF_REJECTED"):
            self.authority.begin_review(c["task_id"], self.owner(subject="attacker"))

    def test_stale_owner_identity_rejected(self):
        c, _ = self.pending()
        old = self.owner(ttl=1)
        self.clock.t += 2
        with self.assertRaisesRegex(Denied, "OWNER_IDENTITY_PROOF_REJECTED"):
            self.authority.begin_review(c["task_id"], old)

    def test_invalid_csrf_rejected_then_genuine_challenge_succeeds(self):
        c, _ = self.pending()
        session = self.owner()
        challenge = self.authority.begin_review(c["task_id"], session)["review_challenge"]
        with self.assertRaisesRegex(Denied, "CSRF_MISMATCH"):
            self.approve(c, token=session, challenge=challenge, csrf="0" * 32)
        self.assertEqual(self.approve(c, token=session, challenge=challenge)[1]["state"], "APPROVED")

    def test_review_challenge_replay_rejected(self):
        c, _ = self.pending()
        session = self.owner()
        ch = self.authority.begin_review(c["task_id"], session)["review_challenge"]
        self.approve(c, token=session, challenge=ch)
        with self.assertRaisesRegex(Denied, "REVIEW_NOT_AUTHORIZED"):
            self.approve(c, token=session, challenge=ch)

    def test_cross_session_challenge_rejected(self):
        c, _ = self.pending()
        session_a, session_b = self.owner(), self.owner()
        ch = self.authority.begin_review(c["task_id"], session_a)["review_challenge"]
        with self.assertRaisesRegex(Denied, "REVIEW_SESSION_INVALID_OR_REPLAYED"):
            self.approve(c, token=session_b, challenge=ch)

    def test_rejection_is_never_a_grant(self):
        c, r = self.approve(decision="reject")
        self.assertEqual(r["state"], "REJECTED")
        with self.assertRaises(Denied):
            self.authority.preview(c["task_id"], action_hash(c))

    def test_approval_expires_at_dispatch(self):
        c, _ = self.approve()
        self.clock.t += 121
        with self.assertRaisesRegex(Denied, "APPROVAL_INVALID_OR_EXPIRED"):
            self.authority.preview(c["task_id"], action_hash(c))

    def test_deleted_audit_event_is_refused(self):
        c, _ = self.pending()
        with closing(sqlite3.connect(self.db)) as db:
            db.execute("DELETE FROM audit WHERE task_id=?", (c["task_id"],))
            db.commit()
        with self.assertRaisesRegex(Denied, "CHECKPOINT_DB_MISMATCH"):
            self.authority.inspect(c["task_id"])

    def test_commit_checkpoint_crash_gap_fails_closed(self):
        c, _ = self.pending()
        with closing(sqlite3.connect(self.db)) as db:
            db.execute("UPDATE intents SET state='APPROVED' WHERE task_id=?", (c["task_id"],))
            db.commit()
        with self.assertRaisesRegex(Denied, "CHECKPOINT_DB_MISMATCH"):
            OwnerAuthorityResearch(self.db, self.root, self.verifier, self.keys[2], clock=self.clock)

    def test_protected_root_wrong_signature_rejected(self):
        with closing(sqlite3.connect(self.root.path)) as db:
            db.execute("UPDATE checkpoints SET mac='" + ("0"*64) + "' WHERE epoch=1")
            db.commit()
        with self.assertRaisesRegex(Denied, "PROTECTED_ROOT_TAMPERED"):
            self.authority.inspect("0"*32)

    def test_no_implicit_rebootstrap_when_authority_db_exists(self):
        with self.assertRaisesRegex(Denied, "NO_AUTO_REBOOTSTRAP"):
            OwnerAuthorityResearch(self.db, self.root, self.verifier, self.keys[2], bootstrap=True)

    def test_estop_persists_across_authority_restart(self):
        c, _ = self.approve()
        self.assertEqual(self.authority.emergency_stop()["estop"], "LATCHED")
        restored = OwnerAuthorityResearch(self.db, self.root, self.verifier,
                                           self.keys[2], clock=self.clock)
        with self.assertRaisesRegex(Denied, "ESTOP_LATCHED"):
            restored.preview(c["task_id"], action_hash(c))

    def test_two_db_rollback_detected_only_with_external_trusted_floor(self):
        first, _ = self.pending()
        old_epoch = self.root.read()[0]
        db_backup = self.folder / "db-backup.sqlite"
        root_backup = self.folder / "root-backup.sqlite"
        for path, backup in ((self.db, db_backup), (self.root.path, root_backup)):
            with closing(sqlite3.connect(path)) as source, closing(sqlite3.connect(backup)) as dest:
                source.backup(dest)
        self.pending()
        trusted_epoch = self.root.read()[0]
        self.assertGreater(trusted_epoch, old_epoch)
        for backup, path in ((db_backup, self.db), (root_backup, self.root.path)):
            with closing(sqlite3.connect(backup)) as source, closing(sqlite3.connect(path)) as dest:
                source.backup(dest)
        # Passing without floor illustrates actual weakness; it is NOT an acceptance.
        insecure_root = ProtectedRootResearch(self.root.path, self.keys[0])
        OwnerAuthorityResearch(self.db, insecure_root, self.verifier, self.keys[2], clock=self.clock)
        protected_floor = ProtectedRootResearch(self.root.path, self.keys[0],
                                                 trusted_min_epoch=trusted_epoch)
        with self.assertRaisesRegex(Denied, "EXTERNAL_EPOCH_ROLLBACK"):
            OwnerAuthorityResearch(self.db, protected_floor, self.verifier, self.keys[2], clock=self.clock)


class ProcessIsolationTests(unittest.TestCase):
    """Real separate OS processes, but all under the same sandbox OS identity."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.keys = [secrets.token_bytes(32) for _ in range(6)]
        self.ctx = mp.get_context("spawn")
        self.rootq = self.ctx.Queue()
        self.authorityq = self.ctx.Queue()
        self.rootprocess = self.ctx.Process(target=root_process, args=(
            str(self.folder / "root.sqlite"), self.keys[0], self.keys[1], self.rootq), daemon=True)
        self.rootprocess.start()
        self.root_addr = self.rootq.get(timeout=15)["root_address"]
        self.ownerprocess = None
        self.start_authority(bootstrap=True)
        self.addCleanup(self.shutdown)

    def start_authority(self, bootstrap=False):
        self.authorityq = self.ctx.Queue()
        self.ownerprocess = self.ctx.Process(target=authority_process, args=(
            str(self.folder / "authority.sqlite"), self.root_addr, self.keys[1],
            self.keys[2], self.keys[3], self.keys[4], self.keys[5], self.authorityq, bootstrap), daemon=True)
        self.ownerprocess.start()
        self.endpoints = self.authorityq.get(timeout=15)
        self.assertNotEqual(self.ownerprocess.pid, self.rootprocess.pid)

    def shutdown(self):
        for p in (self.ownerprocess, self.rootprocess):
            if p is not None:
                if p.is_alive():
                    p.terminate()
                p.join(timeout=5)
                if p.is_alive():
                    p.kill()
                    p.join(timeout=5)

    def agent(self, **req):
        return request(self.endpoints["agent_address"], self.keys[2], req)

    def owner(self, **req):
        return request(self.endpoints["owner_address"], self.keys[3], req)

    def token(self):
        return SyntheticIssuer(self.keys[4]).mint()

    def test_distinct_processes_and_distinct_channel_capabilities(self):
        pid = self.agent(op="pid")
        self.assertTrue(pid["ok"])
        self.assertEqual(pid["data"]["pid"], self.ownerprocess.pid)
        self.assertNotEqual(pid["data"]["pid"], self.rootprocess.pid)
        self.assertNotEqual(pid["data"]["pid"], __import__("os").getpid())
        self.assertFalse(self.agent(op="decide", task_id="a")["ok"])
        with self.assertRaises(AuthenticationError):
            request(self.endpoints["owner_address"], self.keys[2], {"op": "estop"})

    def test_separate_owner_channel_can_approve_only_inert_preview(self):
        c = action()
        proposed = self.agent(op="submit", action=c)
        self.assertTrue(proposed["ok"], proposed)
        proof = self.token()
        challenge = self.owner(op="begin_review", task_id=c["task_id"], identity_proof=proof)
        self.assertTrue(challenge["ok"], challenge)
        ch = challenge["data"]["review_challenge"]
        approved = self.owner(op="decide", task_id=c["task_id"], expected_hash=action_hash(c),
                              decision="approve", identity_proof=proof, challenge=ch, csrf_echo=ch)
        self.assertTrue(approved["ok"], approved)
        result = self.agent(op="preview", task_id=c["task_id"], expected_hash=action_hash(c))
        self.assertTrue(result["ok"], result)
        self.assertFalse(result["data"]["external_effects"])
        self.assertFalse(self.agent(op="preview", task_id=c["task_id"], expected_hash=action_hash(c))["ok"])

    def test_root_process_outage_is_fail_closed(self):
        c = action()
        self.assertTrue(self.agent(op="submit", action=c)["ok"])
        self.rootprocess.terminate(); self.rootprocess.join(timeout=5)
        refused = self.agent(op="inspect", task_id=c["task_id"])
        self.assertFalse(refused["ok"])
        self.assertIn("PROTECTED_ROOT_UNAVAILABLE", refused["error"])

    def test_restarting_owner_process_preserves_approved_grant(self):
        c = action()
        self.assertTrue(self.agent(op="submit", action=c)["ok"])
        proof = self.token()
        ch = self.owner(op="begin_review", task_id=c["task_id"], identity_proof=proof)["data"]["review_challenge"]
        self.assertTrue(self.owner(op="decide", task_id=c["task_id"], expected_hash=action_hash(c),
                                   decision="approve", identity_proof=proof, challenge=ch, csrf_echo=ch)["ok"])
        self.ownerprocess.terminate(); self.ownerprocess.join(timeout=5)
        self.start_authority(bootstrap=False)
        check = self.agent(op="inspect", task_id=c["task_id"])
        self.assertEqual(check["data"]["state"], "APPROVED")
        result = self.agent(op="preview", task_id=c["task_id"], expected_hash=action_hash(c))
        self.assertTrue(result["ok"], result)

    def test_owner_estop_blocks_demo_even_after_process_restart(self):
        c = action()
        self.assertTrue(self.agent(op="submit", action=c)["ok"])
        self.assertTrue(self.owner(op="estop")["ok"])
        self.ownerprocess.terminate(); self.ownerprocess.join(timeout=5)
        self.start_authority(bootstrap=False)
        x = self.agent(op="preview", task_id=c["task_id"], expected_hash=action_hash(c))
        self.assertFalse(x["ok"])
        self.assertIn("ESTOP_LATCHED", x["error"])


if __name__ == "__main__":
    unittest.main()
