"""Negative tests for the shared OFFLINE CI gate; no live Hermes access."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ci_nonacceptance_gate import (
    REVIEWED_PROPERTIES, REQUIRED_FLAGS, SOURCE_NAMES,
    validate_report, discover_tests, main,
)


def valid_fixture() -> dict:
    return {
        "scope": "OFFLINE_STATIC_SOURCE_REVIEW_NOT_RUNTIME_ACCEPTANCE",
        "sources": {
            name: {"status": "PARSED", "sha256": "a" * 64}
            for name in SOURCE_NAMES
        },
        "review_signals": dict(REVIEWED_PROPERTIES),
        "risk_flags": sorted(REQUIRED_FLAGS),
        "assessment": "HOLD", "production": "HOLD",
        "G0": "NO-GO", "G_CODE": "NO-GO", "G1": "NO-GO",
    }


class ContractGateTests(unittest.TestCase):
    def test_verified_static_fixture_still_nonacceptance(self):
        self.assertEqual(validate_report(valid_fixture()), [])

    def test_null_report_fails(self):
        self.assertIn("INVALID_REPORT", validate_report(None))

    def test_scope_mismatch_fails(self):
        r = valid_fixture()
        r["scope"] = "PRODUCTION"
        self.assertIn("INVALID_SCOPE", validate_report(r))

    def test_missing_sources_fails(self):
        r = valid_fixture()
        r["sources"] = []
        self.assertIn("MISSING_SOURCES", validate_report(r))

    def test_every_missing_source_fails(self):
        for name in SOURCE_NAMES:
            with self.subTest(name=name):
                r = valid_fixture()
                r["sources"].pop(name)
                self.assertIn("SOURCE_NOT_PARSED:" + name, validate_report(r))

    def test_source_unparsed_fails(self):
        r = valid_fixture()
        r["sources"]["docker"]["status"] = "MISSING"
        self.assertIn("SOURCE_NOT_PARSED:docker", validate_report(r))

    def test_source_unpinned_fails(self):
        r = valid_fixture()
        r["sources"]["estop"]["sha256"] = "unverified"
        self.assertIn("SOURCE_NOT_PINNED:estop", validate_report(r))

    def test_absent_properties_fail(self):
        r = valid_fixture()
        r["review_signals"] = {}
        failures = validate_report(r)
        self.assertTrue(any(f.startswith("SOURCE_CONTRACT_DRIFT:") for f in failures))

    def test_secure_default_change_still_requires_review(self):
        r = valid_fixture()
        r["review_signals"]["docker_default_network"] = False
        self.assertIn("SOURCE_CONTRACT_DRIFT:docker_default_network", validate_report(r))

    def test_undocumented_estop_scope_fails(self):
        r = valid_fixture()
        r["review_signals"]["estop_new_work_only_documented"] = "UNKNOWN"
        self.assertIn("SOURCE_CONTRACT_DRIFT:estop_new_work_only_documented", validate_report(r))

    def test_all_missing_risk_flags_fail(self):
        r = valid_fixture()
        r["risk_flags"] = []
        failures = validate_report(r)
        self.assertEqual(len([x for x in failures if x.startswith("RISK_FLAG_MISSING:")]), len(REQUIRED_FLAGS))

    def test_risk_flags_malformed_fail(self):
        r = valid_fixture()
        r["risk_flags"] = {"all": "ok"}
        self.assertIn("MALFORMED_RISK_FLAGS", validate_report(r))

    def test_gate_forgery_fails(self):
        for key in ("assessment", "production", "G0", "G_CODE", "G1"):
            with self.subTest(key=key):
                r = valid_fixture()
                r[key] = "GO"
                self.assertIn("INVALID_GATE:" + key, validate_report(r))

    def test_unrelated_extra_flags_do_not_erase_blockers(self):
        r = valid_fixture()
        r["risk_flags"].append("ADDITIONAL_RISK")
        self.assertEqual(validate_report(r), [])


class DiscoveryGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tests = self.root / "tests"
        self.tests.mkdir()
        # Python 3.12 requires discoverable temporary dirs to be importable.
        (self.tests / "__init__.py").write_text("", encoding="utf-8")

    def write_suite(self, count: int):
        # Unique module names prevent unittest/sys.modules collisions across fixtures.
        name = "test_fixture_" + self.root.name.replace("-", "_") + ".py"
        file = self.tests / name
        file.write_text(
            "import unittest\n"
            "class Fixture(unittest.TestCase): pass\n"
            "for index in range(" + str(count) + "):\n"
            "    setattr(Fixture, 'test_%03d' % index, lambda self: self.assertTrue(True))\n",
            encoding="utf-8",
        )

    def test_floor_cannot_be_lowered(self):
        self.write_suite(154)
        with self.assertRaisesRegex(ValueError, "floor"):
            discover_tests(self.tests, 153)

    def test_count_below_floor_fails(self):
        self.write_suite(153)
        with self.assertRaisesRegex(ValueError, "below"):
            discover_tests(self.tests, 154)

    def test_valid_synthetic_count(self):
        self.write_suite(154)
        self.assertEqual(discover_tests(self.tests, 154), 154)

    def test_missing_tree_fails(self):
        with self.assertRaisesRegex(ValueError, "tree"):
            discover_tests(self.root / "absent", 154)

    def test_cli_production_hold_on_missing_sources(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["--source-root", str(self.root)])
        payload = json.loads(out.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "SAFE_STOP")
        self.assertEqual(payload["production"], "HOLD")
        self.assertFalse(payload["host_verified"])


if __name__ == "__main__":
    unittest.main()
