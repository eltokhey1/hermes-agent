"""Offline integration tests for supervisor v2 candidate (no worker invocation)."""
import importlib.util
import pathlib
import subprocess
import sys
import unittest
from unittest.mock import patch

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("supervisor_v2", HERE / "hermes_bridge_supervisor_v2_candidate.py")
supervisor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supervisor)


class SupervisorV2IntegrationTests(unittest.TestCase):
    def test_nonzero_exit_classified_without_stderr(self):
        result = subprocess.CompletedProcess([], 1, stdout="", stderr="gho_sensitive")
        with patch.object(supervisor.subprocess, "run", return_value=result):
            self.assertEqual(supervisor.run_once("dummy"), (1, "WORKER_EXIT_1"))

    def test_success(self):
        result = subprocess.CompletedProcess([], 0, stdout="SCAN_DONE processed=0\n", stderr="")
        with patch.object(supervisor.subprocess, "run", return_value=result):
            self.assertEqual(supervisor.run_once("dummy"), (0, "SCAN_OK"))

    def test_timeout(self):
        with patch.object(supervisor.subprocess, "run", side_effect=subprocess.TimeoutExpired([], 120)):
            self.assertEqual(supervisor.run_once("dummy"), (124, "WORKER_TIMEOUT"))

    def test_os_error(self):
        with patch.object(supervisor.subprocess, "run", side_effect=OSError("secret")):
            self.assertEqual(supervisor.run_once("dummy"), (125, "WORKER_OS_ERROR"))

    def test_success_with_stderr_refused(self):
        result = subprocess.CompletedProcess([], 0, stdout="SCAN_DONE processed=0\n", stderr="secret")
        with patch.object(supervisor.subprocess, "run", return_value=result):
            self.assertEqual(supervisor.run_once("dummy"), (126, "SCAN_STDERR_UNEXPECTED"))

    def test_unknown_output_refused(self):
        result = subprocess.CompletedProcess([], 0, stdout="unexpected", stderr="")
        with patch.object(supervisor.subprocess, "run", return_value=result):
            self.assertEqual(supervisor.run_once("dummy"), (126, "SCAN_OUTPUT_UNKNOWN"))


if __name__ == "__main__":
    unittest.main()
