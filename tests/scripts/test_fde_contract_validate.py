"""Pure validation tests; no subprocess, network, or host environment mutation."""

import contextlib
import copy
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts.fde_contract_validate import main, validate_receipt, verify_artifacts


class FDEContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.contents = b"sanitized local acceptance-test fixture\\n"
        (self.root / "test-evidence.txt").write_bytes(self.contents)
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
                    "artifact_path": "test-evidence.txt",
                    "artifact_sha256": hashlib.sha256(self.contents).hexdigest(),
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

    def test_artifact_path_required(self):
        del self.receipt["checks"][0]["artifact_path"]
        self.assertTrue(any("artifact_path" in e for e in validate_receipt(self.receipt)))

    def test_traversal_and_windows_paths_rejected(self):
        for value in ("../secret.txt", "folder/../secret", "/etc/passwd", "C:\\\\temp\\\\file", "a//b", "a/./b"):
            with self.subTest(path=value):
                self.receipt["checks"][0]["artifact_path"] = value
                self.assertTrue(any("artifact_path" in e for e in validate_receipt(self.receipt)))

    def test_sha256_content_tampering_blocks(self):
        (self.root / "test-evidence.txt").write_bytes(b"modified")
        self.assertTrue(any("SHA-256 mismatch" in e for e in verify_artifacts(self.receipt, self.root)))

    def test_missing_artifact_blocks(self):
        (self.root / "test-evidence.txt").unlink()
        self.assertTrue(verify_artifacts(self.receipt, self.root))

    def test_symlink_artifact_blocks(self):
        (self.root / "test-evidence.txt").unlink()
        try:
            (self.root / "test-evidence.txt").symlink_to(self.root / "elsewhere")
        except (OSError, NotImplementedError):
            self.skipTest("host does not permit symlink creation")
        self.assertTrue(verify_artifacts(self.receipt, self.root))

    def test_no_evidence_root_fails_closed(self):
        receipt_path = self.root / "receipt.json"
        receipt_path.write_text(json.dumps(self.receipt), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            code = main([str(receipt_path)])
        self.assertEqual(code, 1)
        self.assertIn("VERDICT=NOT_READY", stdout.getvalue())

    def test_main_local_artifact_validation(self):
        receipt_path = self.root / "receipt.json"
        receipt_path.write_text(json.dumps(self.receipt), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            code = main([str(receipt_path), "--evidence-root", str(self.root)])
        self.assertEqual(code, 0)
        self.assertIn("PRODUCTION_APPROVED=NO", stdout.getvalue())

    def test_cli_tampering_fails_closed(self):
        receipt_path = self.root / "receipt.json"
        receipt_path.write_text(json.dumps(self.receipt), encoding="utf-8")
        (self.root / "test-evidence.txt").write_bytes(b"tampered")
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            code = main([str(receipt_path), "--evidence-root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("SHA-256 mismatch", stdout.getvalue())

    def test_artifact_digest_match_is_not_release_approval(self):
        self.assertEqual(validate_receipt(self.receipt), [])
        self.assertEqual(verify_artifacts(self.receipt, self.root), [])


if __name__ == "__main__":
    unittest.main()
