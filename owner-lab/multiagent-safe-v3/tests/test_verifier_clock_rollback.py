"""Synthetic-only, in-process clock rollback containment tests.

A new process or first-use verification still needs trusted off-host time.
"""
import unittest
from approvals import ApprovalDenied, ApprovalIssuer, ApprovalVerifier

class FakeClock:
    def __init__(self):
        self.now = 1800000000
    def __call__(self):
        return self.now

class TestVerifierRollbackFence(unittest.TestCase):
    def setUp(self):
        self.clock=FakeClock()
        self.key=b"synthetic-only-approval-test-key-32bytes"
        self.verifier=ApprovalVerifier(self.key, clock=self.clock)
        self.token=ApprovalIssuer(self.key,clock=self.clock).issue(
            task_id="a"*32,spec_hash="b"*64,approver="synthetic-only",
            decision="approve",ttl_seconds=2)

    def check(self):
        return self.verifier.verify(self.token, task_id="a"*32, spec_hash="b"*64)

    def test_expired_then_rolled_back_clock_stays_denied(self):
        self.clock.now+=3
        with self.assertRaises(ApprovalDenied):
            self.check()
        self.clock.now-=2
        with self.assertRaises(ApprovalDenied):
            self.check()

    def test_forward_progress_remains_valid_and_backward_step_denied(self):
        self.assertEqual("approve",self.check()["decision"])
        self.clock.now+=1
        self.assertEqual("approve",self.check()["decision"])
        self.clock.now-=1
        with self.assertRaises(ApprovalDenied):
            self.check()

    def test_invalid_clock_cannot_reset_rollback_fence(self):
        self.clock.now+=3
        with self.assertRaises(ApprovalDenied):
            self.check()
        self.clock.now=float("nan")
        with self.assertRaises(ApprovalDenied):
            self.check()
        self.clock.now=1800000001
        with self.assertRaises(ApprovalDenied):
            self.check()
