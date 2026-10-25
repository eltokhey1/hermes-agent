"""Behavior tests for the strict CI aggregate gate (scripts/ci/required_results.py)."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "required_results.py"

_spec = importlib.util.spec_from_file_location("required_results", SCRIPT)
required_results = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(required_results)

evaluate_gate = required_results.evaluate_gate


import pytest


@pytest.mark.parametrize("release", [False, True])
@pytest.mark.parametrize("job", ["tests", "osv-scanner", "history-check", "e2e-desktop"])
@pytest.mark.parametrize("result,ordinary,excluded", [
    ("success", True, True), ("skipped", False, True), ("failure", False, False),
    ("cancelled", False, False), ("with-status", False, False),
    ("action_required", False, False), ("unknown", False, False), (None, False, False),
])
def test_status_policy(job, result, ordinary, excluded, release):
    expected = excluded if job in ("history-check", "e2e-desktop") else ordinary
    if result == "skipped" and not release:
        expected = True
    verdict = evaluate_gate({job: {} if result is None else {"result": result}}, release=release)
    assert verdict == {"ok": expected, "failed": [] if expected else [job],
                       "allowed_skips": [job] if expected and result == "skipped" else []}


@pytest.mark.parametrize("lane,jobs", [
    ("python", ("tests", "tests-os")),
    ("frontend", ("js-tests",)),
    ("e2e", ("tests", "tests-os")),
    ("e2e_upgrade", ("tests", "tests-os")),
    ("desktop_updater", ("tests-os",)),
    ("e2e_desktop_core", ("e2e-desktop-core",)),
    ("e2e_desktop_update", ("e2e-desktop-update",)),
    ("remote_backends", ("remote-backends",)),
    ("catalog", ("catalog-tests",)),
])
@pytest.mark.parametrize("result", ["skipped", "absent", "success"])
def test_selected_update_consumers_must_succeed(lane, jobs, result):
    needs = {"detect": {"result": "success", "outputs": {lane: "true"}}}
    if result != "absent":
        needs.update({job: {"result": result} for job in jobs})
    verdict = evaluate_gate(needs)
    assert verdict["ok"] is (result == "success")
    assert verdict["failed"] == ([] if result == "success" else sorted(jobs))
    assert verdict["allowed_skips"] == []
    # False string outputs must not arm a job merely because they are truthy.
    needs["detect"]["outputs"][lane] = "false"
    assert evaluate_gate(needs)["ok"]



@pytest.mark.parametrize("release", [False, True])
def test_skipped_classifier_is_never_accepted(release):
    # The change classifier is required to select the test matrix. A skipped
    # classifier must not be silently treated as an allowed PR skip.
    needs = {"detect": {"result": "skipped"}, "tests": {"result": "success"}}
    assert evaluate_gate(needs, release=release) == {
        "ok": False, "failed": ["detect"], "allowed_skips": [],
    }


def test_entirely_skipped_pr_cannot_report_green():
    # Regression: the old PR gate returned ok=True for this input.
    needs = {name: {"result": "skipped"} for name in ("detect", "tests", "lint")}
    verdict = evaluate_gate(needs, release=False)
    assert verdict == {
        "ok": False, "failed": ["detect"],
        "allowed_skips": ["lint", "tests"],
    }


@pytest.mark.parametrize("release", [False, True])
@pytest.mark.parametrize("outputs", [
    {},
    {"python": "", "frontend": "", "event_name": "pull_request"},
    {"event_name": "pull_request"},
])
def test_classifier_success_without_usable_lane_outputs_fails_closed(release, outputs):
    # A classifier job may succeed but publish no valid booleans. Downstream
    # jobs then skip and the former aggregate gate falsely returned green.
    needs = {
        "detect": {"result": "success", "outputs": outputs},
        "tests": {"result": "skipped"},
        "tests-os": {"result": "skipped"},
    }
    verdict = evaluate_gate(needs, release=release)
    assert verdict["ok"] is False
    assert "detect:outputs-unusable" in verdict["failed"]


def test_all_false_classifier_outputs_are_valid_for_unrelated_changes():
    # A no-op classification is distinct from broken or absent outputs.
    needs = {
        "detect": {"result": "success", "outputs": {"python": "false", "frontend": "false"}},
        "tests": {"result": "skipped"},
    }
    verdict = evaluate_gate(needs)
    assert verdict["ok"] is True
    assert verdict["allowed_skips"] == ["tests"]


def test_release_exclusion_policy():
    assert required_results.EXCLUDED_JOBS == {
        "history-check", "lockfile-diff", "prompt-surface-diff", "supply-chain", "e2e-desktop",
    }


@pytest.mark.parametrize("needs", [{}, None])
@pytest.mark.parametrize("release", [False, True])
def test_empty_needs_fails_closed(needs, release):
    assert evaluate_gate(needs, release=release) == {
        "ok": False, "failed": ["<no-needs>"], "allowed_skips": [],
    }
    assert required_results.compact_results(needs) == {}


@pytest.mark.parametrize("release,results,code,report", [
    (True, {"detect": "success", "e2e-desktop": "skipped"}, 0, "All checks passed"),
    (True, {"tests": "skipped", "history-check": "skipped", "lint": "failure"},
     1, "::error::2 job(s) failed: lint, tests"),
    (False, {"tests": "failure"}, 1, "::error::1 job(s) failed: tests"),
])
def test_cli_stdin_exit_codes_and_output(tmp_path, release, results, code, report):
    output = tmp_path / "github-output.txt"
    needs = {name: {"result": result, "outputs": {"detail": "kept",
             **({"python": "false"} if name == "detect" else {})}}
             for name, result in results.items()}
    child = subprocess.run(
        [sys.executable, str(SCRIPT), *(["--release"] if release else [])],
        input=json.dumps(needs), capture_output=True, text=True, timeout=30,
        env={**os.environ, "GITHUB_OUTPUT": str(output)},
        check=False,
    )
    assert child.returncode == code, child.stderr
    assert report in child.stdout
    key, value = output.read_text(encoding="utf-8-sig").strip().split("=", 1)
    assert key == "needs-json"
    assert json.loads(value) == results
    assert f"{key}={value}" in child.stdout
    for name, result in results.items():
        assert f"{name}: {result}" in child.stdout


@pytest.mark.parametrize("results,expected_rc", [
    ({"tests": "success"}, 0),
    ({"detect": "success", "tests": "failure", "history-check": "skipped"}, 1),
])
def test_cli_cp1252_console_preserves_verdict_without_unicode_crash(tmp_path, results, expected_rc):
    """The required CI gate must emit a verdict on non-UTF8 Windows consoles."""
    output = tmp_path / "strict-gate-output.txt"
    needs = {name: {"result": result,
             **({"outputs": {"python": "false"}} if name == "detect" else {})}
             for name, result in results.items()}
    child = subprocess.run(
        [sys.executable, str(SCRIPT), "--release"],
        input=json.dumps(needs),
        capture_output=True,
        text=True,
        encoding="cp1252",
        timeout=30,
        env={**os.environ, "GITHUB_OUTPUT": str(output), "PYTHONIOENCODING": "cp1252:strict"},
        check=False,
    )
    assert child.returncode == expected_rc, child.stderr
    assert "UnicodeEncodeError" not in child.stderr
    assert output.exists()
    compact = json.loads(output.read_text(encoding="utf-8").strip().split("=", 1)[1])
    assert compact == results
    if expected_rc:
        assert "[FAIL] tests: failure" in child.stdout
        assert "[SKIP] history-check: skipped" in child.stdout
        assert "::error::1 job(s) failed: tests" in child.stdout
    else:
        assert "[PASS] tests: success" in child.stdout
        assert "All checks passed" in child.stdout
