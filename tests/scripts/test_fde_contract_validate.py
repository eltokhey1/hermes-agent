"""Pure validation tests; no subprocess, network, or host environment mutation."""

import copy
import unittest

from scripts.fde_contract_validate import validate_receipt


class FDEContractTests(unittest.TestCase):
    def setUp(self):
        self.receipt = {
            "schema_version": 1,
            "project_id": "shipment-eta-audit",
            "scope": "offline comparison of ship ETA evidence",
            "base_commit": "a" * 40,
            "environment": "sandbox",
            "observed_at": "2026-10-18T08:30:00+02:00",
            "release": {"intent": "review_only", "production_approved": False},
            "checks": [
                {
                    "gate": gate,
                    "status": "PASS",
                    "description": "Locally observed fixture, subject to independent review",
                    "command": "python -m unittest discover -s tests/scripts",
                    "exit_code": 0,
                    "artifact_sha256": "b" * 64,
                    "observed_at": "2026-10-18T08:30:00+02:00",
                }
                for gate in ("security", "recovery", "idempotency", "privacy", "quality")
            ],
        }

    def test_valid_receipt_shape_not_release_approval(self):
        self.assertEqual(validate_receipt(self.receipt), [])

    def test_missing_gate_blocks(self):
        self.receipt["checks"].pop()
        self.assertTrue(any("missing required gates" in e for e in validate_receipt(self.receipt)))

    def test_unknown_gate_blocks(self):
        self.receipt["checks"][0]["status"] = "UNKNOWN"
        self.assertTrue(any("not PASS" in e for e in validate_receipt(self.receipt)))

    def test_invalid_hash_blocks(self):
        self.receipt["checks"][0]["artifact_sha256"] = "not-a-hash"
        self.assertTrue(any("SHA-256" in e for e in validate_receipt(self.receipt)))

    def test_duplicate_gate_blocks(self):
        self.receipt["checks"].append(copy.deepcopy(self.receipt["checks"][0]))
        self.assertTrue(any("duplicated" in e for e in validate_receipt(self.receipt)))

    def test_production_approval_is_not_self_issued(self):
        self.receipt["release"]["production_approved"] = True
        self.assertTrue(any("production_approved" in e for e in validate_receipt(self.receipt)))

    def test_timezones_required(self):
        self.receipt["observed_at"] = "2026-10-18T08:30:00"
        self.assertTrue(any("timezone" in e for e in validate_receipt(self.receipt)))

    def test_bool_exit_code_not_accepted(self):
        self.receipt["checks"][0]["exit_code"] = False
        self.assertTrue(any("exit_code" in e for e in validate_receipt(self.receipt)))

    def test_nonpass_cannot_claim_exit_zero(self):
        self.receipt["checks"][0]["status"] = "FAIL"
        self.assertTrue(any("non-PASS" in e for e in validate_receipt(self.receipt)))

    def test_bad_top_level_type(self):
        self.assertTrue(validate_receipt([]))

    def test_unhashable_untrusted_json_values_do_not_crash(self):
        self.receipt["environment"] = []
        self.receipt["checks"][0]["status"] = []
        self.assertTrue(validate_receipt(self.receipt))

    def test_float_schema_version_not_accepted(self):
        self.receipt["schema_version"] = 1.0
        self.assertTrue(any("schema_version" in e for e in validate_receipt(self.receipt)))


if __name__ == "__main__":
    unittest.main()
