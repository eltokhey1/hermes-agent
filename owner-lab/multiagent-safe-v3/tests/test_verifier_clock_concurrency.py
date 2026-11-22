"""Deterministic synthetic two-thread check of verifier clock ordering.

The injected clock models two valid reads performed in chronological order,
whose Python callbacks return in reverse order due to a context switch.
"""
import threading
import unittest
from approvals import ApprovalDenied, ApprovalIssuer, ApprovalVerifier

_KEY = b"synthetic-only-approval-test-key-32bytes"
_TASK = "a" * 32
_SPEC = "b" * 64
_START = 1800000000

class DelayedOrderedClock:
    def __init__(self):
        self.count = 0
        self.counter_lock = threading.Lock()
        self.first_called = threading.Event()
        self.second_called = threading.Event()
        self.release_first = threading.Event()

    def __call__(self):
        with self.counter_lock:
            self.count += 1
            index = self.count
        if index == 1:
            self.first_called.set()
            if not self.release_first.wait(3):
                raise RuntimeError("Synthetic clock stalled")
            return _START
        self.second_called.set()
        return _START + 1

class TestVerifierClockConcurrent(unittest.TestCase):
    def test_two_valid_concurrent_calls_do_not_false_deny(self):
        clock = DelayedOrderedClock()
        token = ApprovalIssuer(_KEY, clock=lambda: _START).issue(
            task_id=_TASK, spec_hash=_SPEC, approver="synthetic",
            decision="approve", ttl_seconds=40,
        )
        verifier = ApprovalVerifier(_KEY, clock=clock)
        outcomes = {}

        def worker(name):
            try:
                verifier.verify(token, task_id=_TASK, spec_hash=_SPEC)
                outcomes[name] = "APPROVED"
            except ApprovalDenied:
                outcomes[name] = "DENIED"
            except Exception:
                outcomes[name] = "ERROR"

        first = threading.Thread(target=worker, args=("first",))
        second = threading.Thread(target=worker, args=("second",))
        first.start()
        try:
            self.assertTrue(clock.first_called.wait(2))
            second.start()
            clock.second_called.wait(0.25)
        finally:
            clock.release_first.set()
            first.join(4)
            if second.ident is not None:
                second.join(4)
        self.assertFalse(first.is_alive() or second.is_alive())
        self.assertEqual(2, clock.count)
        self.assertEqual({"first": "APPROVED", "second": "APPROVED"}, outcomes)
