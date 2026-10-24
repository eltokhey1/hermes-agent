"""Fork-safe, stdlib-only checks for the real CI classifier and strict gate.

These are *supplementary* checks when the upstream Blacksmith runner pool is
unavailable, never replacements for the repo's full required CI jobs.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(relpath: str, name: str):
    path = ROOT / relpath
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ForkCiSanity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.classifier = load("scripts/ci/classify_changes.py", "owner_fork_classifier")
        cls.gate = load("scripts/ci/required_results.py", "owner_fork_strict_gate")

    def test_python_source_arms_python_checks(self):
        result = self.classifier.classify(["run_agent.py"])
        self.assertIs(result["python"], True)
        self.assertIs(result["python_prod"], True)

    def test_test_only_change_does_not_arm_production_python(self):
        result = self.classifier.classify(["tests/ci/test_owner_fork_ci_sanity.py"])
        self.assertIs(result["python"], True)
        self.assertIs(result["python_prod"], False)

    def test_required_gate_fails_if_selected_python_lane_skipped(self):
        result = self.gate.evaluate_gate({
            "detect": {"result": "success", "outputs": {"python": "true"}},
            "tests": {"result": "skipped"},
            "tests-os": {"result": "skipped"},
        })
        self.assertIs(result["ok"], False)
        self.assertIn("tests", result["failed"])
        self.assertIn("tests-os", result["failed"])

    def test_required_gate_fails_closed_for_missing_needs(self):
        self.assertIs(self.gate.evaluate_gate({})["ok"], False)
        self.assertIs(self.gate.evaluate_gate(None)["ok"], False)

    def test_classifier_on_standard_runner_preserves_full_gate(self):
        text = (ROOT / ".github/workflows/ci.yaml").read_text(encoding="utf-8")
        detect = text.split("\n  detect:", 1)[1].split("\n  tests:", 1)[0]
        self.assertIn("runs-on: ubuntu-latest", detect)
        self.assertIn("actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683", detect)
        self.assertIn("name: All required checks pass", text)
        self.assertIn("scripts/ci/required_results.py", text)
        self.assertIn("uses: ./.github/workflows/tests.yml", text)


if __name__ == "__main__":
    unittest.main()
