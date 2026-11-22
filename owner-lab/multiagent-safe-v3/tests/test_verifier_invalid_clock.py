import unittest
from approvals import ApprovalIssuer, ApprovalVerifier, ApprovalDenied

class VerifierClockGuardTests(unittest.TestCase):
    def setUp(self):
        self.key=b"synthetic-only-approval-test-key-32bytes"
        self.issued_at=1800000000
        self.task_id="a"*32
        self.spec_hash="b"*64
        self.token=ApprovalIssuer(self.key,clock=lambda: self.issued_at).issue(
            task_id=self.task_id,spec_hash=self.spec_hash,
            approver="synthetic-reviewer",decision="approve",ttl_seconds=2)

    def verify_with(self,clock_value):
        return ApprovalVerifier(self.key,clock=lambda: clock_value).verify(
            self.token,task_id=self.task_id,spec_hash=self.spec_hash)

    def test_expired_token_with_nan_clock_is_rejected(self):
        with self.assertRaises(ApprovalDenied):
            self.verify_with(float("nan"))

    def test_malformed_clock_types_are_rejected_without_crash(self):
        for value in (None,True,"broken-clock",object()):
            with self.subTest(value=repr(value)),self.assertRaises(ApprovalDenied):
                self.verify_with(value)

    def test_infinite_clock_values_rejected(self):
        for value in (float("inf"),float("-inf")):
            with self.subTest(value=value),self.assertRaises(ApprovalDenied):
                self.verify_with(value)

    def test_finite_clock_validity_and_expiry_preserved(self):
        self.assertEqual("approve",self.verify_with(self.issued_at)["decision"])
        with self.assertRaises(ApprovalDenied):
            self.verify_with(self.issued_at+3)
