"""Read-only static runner inventory must never be mistaken for CI acceptance."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts/ci/audit_runner_portability.py"
spec = importlib.util.spec_from_file_location("owner_fork_runner_audit", MODULE)
assert spec is not None and spec.loader is not None
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)


class ForkRunnerInventoryTests(unittest.TestCase):
    def test_fixture_counts_per_file_not_per_mention(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            folder = root / ".github/workflows"
            folder.mkdir(parents=True)
            (folder / "one.yml").write_text(
                "runs-on: blacksmith-4vcpu-ubuntu-2404\n"
                "# mention blacksmith-4vcpu-ubuntu-2404 again\n", encoding="utf-8")
            (folder / "two.yaml").write_text(
                "runs-on: windows-latest-32-arm-core\n", encoding="utf-8")
            result = audit_module.audit(root)
            self.assertEqual(2, result["workflow_files_scanned"])
            refs = result["special_runner_references"]
            self.assertEqual(1, refs["blacksmith-4vcpu-ubuntu-2404"]["file_count"])
            self.assertEqual(1, refs["windows-latest-32-arm-core"]["file_count"])
            self.assertEqual("NOT_ATTESTED", result["strict_ci_passed"])
            self.assertEqual("NOT_ATTESTED", result["runner_pool_available"])
            self.assertTrue(result["read_only"])

    def test_fails_if_workflows_missing(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                audit_module.audit(Path(t))

    def test_actual_upstream_runner_dependencies_are_visible(self):
        result = audit_module.audit(ROOT)
        self.assertGreater(result["workflow_files_scanned"], 15)
        refs = result["special_runner_references"]
        self.assertIn("blacksmith-4vcpu-ubuntu-2404", refs)
        self.assertNotIn(".github/workflows/ci.yaml", refs["blacksmith-4vcpu-ubuntu-2404"]["files"])

    def test_classifier_is_portable_but_not_entire_pipeline(self):
        source = (ROOT / ".github/workflows/ci.yaml").read_text(encoding="utf-8")
        detect = source.split("\n  detect:", 1)[1].split("\n  tests:", 1)[0]
        self.assertIn("runs-on: ubuntu-latest", detect)
        self.assertIn("actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683", detect)
        self.assertNotIn("runs-on: blacksmith-", detect)
        self.assertIn("uses: ./.github/workflows/tests.yml", source)


    def test_strict_gate_is_hosted_without_weakening_aggregation(self):
        # A required result gate must not depend on an unavailable third-party
        # runner, while still evaluating every selected job and strict release.
        source = (ROOT / ".github/workflows/ci.yaml").read_text(encoding="utf-8")
        gate = source.split("\n  all-checks-pass:", 1)[1].split("\n  ci-timings:", 1)[0]
        self.assertIn("runs-on: ubuntu-latest", gate)
        self.assertNotIn("runs-on: blacksmith-", gate)
        self.assertIn("actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683", gate)
        self.assertIn("persist-credentials: false", gate)
        self.assertNotIn("useblacksmith/checkout@", gate)
        self.assertIn("if: always()", gate)
        self.assertIn("needs:", gate)
        self.assertIn("scripts/ci/required_results.py", gate)
        self.assertIn("RELEASE: ${{ inputs.release }}", gate)
        self.assertIn("NEEDS: ${{ toJSON(needs) }}", gate)


    def test_advisory_timing_job_uses_hosted_runner_not_approval_bypass(self):
        source = (ROOT / ".github/workflows/ci.yaml").read_text(encoding="utf-8")
        timing = source.split("\n  ci-timings:", 1)[1]
        self.assertIn("runs-on: ubuntu-latest", timing)
        self.assertNotIn("runs-on: blacksmith-", timing)
        self.assertIn("actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683", timing)
        self.assertIn("persist-credentials: false", timing)
        self.assertIn("needs: [all-checks-pass]", timing)
        self.assertIn("scripts/ci/timings_report.py", timing)
        self.assertNotIn("useblacksmith/checkout@", timing)



    def test_nix_classifier_is_hosted_but_build_remains_real(self):
        source = (ROOT / ".github/workflows/nix.yml").read_text(encoding="utf-8")
        detect = source.split("\n  detect:", 1)[1].split("\n  flake-check:", 1)[0]
        build = source.split("\n  flake-check:", 1)[1]
        self.assertIn("runs-on: ubuntu-latest", detect)
        self.assertIn("actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683", detect)
        self.assertIn("persist-credentials: false", detect)
        self.assertIn("needs: [detect]", build)
        self.assertIn("runs-on: blacksmith-32vcpu-ubuntu-2404", build)
        self.assertIn("nix flake check", build)

    def test_docker_control_jobs_hosted_but_build_and_publish_are_not_bypassed(self):
        source = (ROOT / ".github/workflows/docker.yml").read_text(encoding="utf-8")
        mode = source.split("\n  mode:", 1)[1].split("\n  detect:", 1)[0]
        detect = source.split("\n  detect:", 1)[1].split("\n  build:", 1)[0]
        build = source.split("\n  build:", 1)[1].split("\n  publish:", 1)[0]
        publish = source.split("\n  publish:", 1)[1].split("\n  merge:", 1)[0]
        self.assertIn("runs-on: ubuntu-latest", mode)
        self.assertIn("runs-on: ubuntu-latest", detect)
        self.assertIn("actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683", detect)
        self.assertIn("persist-credentials: false", detect)
        self.assertIn("needs: [mode, detect]", build)
        self.assertIn("github.repository == 'NousResearch/hermes-agent'", build)
        self.assertIn("runs-on: ${{ matrix.runner }}", build)
        self.assertIn("github.repository == 'NousResearch/hermes-agent'", publish)
        self.assertIn("environment: container-publish", publish)



if __name__ == "__main__":
    unittest.main()
