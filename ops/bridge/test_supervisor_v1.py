"""Synthetic checks for supervisor; no real gh, network, or Aider use."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest.mock import patch

import hermes_bridge_supervisor_v1 as s


class SupervisorTests(unittest.TestCase):
    def test_01_hash_rejects_wrong_worker(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "worker.py"
            p.write_text("print(123)\n")
            with self.assertRaisesRegex(ValueError, "HASH_MISMATCH"):
                s.check_worker(p)

    def test_02_missing_worker_refused(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(s.main(["--worker", str(Path(td)/"missing.py")]), 2)

    def test_03_empty_worker_refused(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "empty.py"; p.write_bytes(b"")
            with self.assertRaises(ValueError): s.check_worker(p)

    def test_04_oversize_worker_refused(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "worker.py"; p.write_bytes(b"x" * 100001)
            with self.assertRaisesRegex(ValueError, "FILE_INVALID"): s.check_worker(p)

    def test_05_interval_too_short(self):
        with self.assertRaises(SystemExit) as cm: s.main(["--interval", "1"])
        self.assertEqual(cm.exception.code, 2)

    def test_06_interval_too_long(self):
        with self.assertRaises(SystemExit) as cm: s.main(["--interval", "3601"])
        self.assertEqual(cm.exception.code, 2)

    def test_07_success_scans(self):
        fake = types.SimpleNamespace(returncode=0, stdout="SCAN_DONE processed=1\n", stderr="")
        with patch.object(s.subprocess, "run", return_value=fake) as call:
            code, label = s.run_once(Path("/fake/worker.py"))
        self.assertEqual((code, label), (0, "SCAN_OK"))
        self.assertEqual(call.call_args.args[0][1:4], ["-I", "-B", "-S"])

    def test_08_inbox_missing_success(self):
        fake = types.SimpleNamespace(returncode=0, stdout="INBOX_MISSING; no action", stderr="")
        with patch.object(s.subprocess, "run", return_value=fake):
            self.assertEqual(s.run_once(Path("/fake/worker.py")), (0, "SCAN_OK"))

    def test_09_unknown_worker_output_fail_closed_label(self):
        fake = types.SimpleNamespace(returncode=0, stdout="", stderr="")
        with patch.object(s.subprocess, "run", return_value=fake):
            self.assertEqual(s.run_once(Path("/fake/worker.py")), (126, "SCAN_OUTPUT_UNKNOWN"))

    def test_10_nonzero(self):
        fake = types.SimpleNamespace(returncode=4, stdout="", stderr="transport failed")
        with patch.object(s.subprocess, "run", return_value=fake):
            self.assertEqual(s.run_once(Path("/fake/worker.py")), (4, "WORKER_EXIT_NONZERO"))

    def test_11_timeout(self):
        with patch.object(s.subprocess, "run", side_effect=subprocess.TimeoutExpired("python", 120)):
            self.assertEqual(s.run_once(Path("/fake/worker.py")), (124, "WORKER_TIMEOUT"))

    def test_12_missing_interpreter(self):
        with patch.object(s.subprocess, "run", side_effect=OSError("executable missing")):
            self.assertEqual(s.run_once(Path("/fake/worker.py")), (125, "WORKER_OS_ERROR"))

    def test_13_atomic_status(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            s.write_status(root, state="HEALTHY", last_exit_code=0)
            data = json.loads((root / "status.json").read_text())
            self.assertEqual(data["production"], "HOLD")
            self.assertEqual(data["state"], "HEALTHY")
            self.assertFalse(list(root.glob("status.*.tmp")))

    def test_14_status_keeps_last_value(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            s.write_status(root, state="DEGRADED")
            s.write_status(root, state="HEALTHY")
            self.assertEqual(json.loads((root/"status.json").read_text())["state"], "HEALTHY")

    def test_15_once_no_network_when_refused(self):
        with patch.object(s, "check_worker", side_effect=ValueError("BAD_HASH")):
            with patch.object(s, "run_once") as run:
                self.assertEqual(s.main(["--worker", "invalid.py"]), 2)
                run.assert_not_called()

    def test_16_one_scan_exit(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "worker.py"
            source.write_text("# fake worker\n")
            with patch.object(s, "check_worker", return_value=source), patch.object(s, "WORKER_SHA256", hashlib.sha256(source.read_bytes()).hexdigest()), patch.object(s, "STATE_DIR", Path(td)), patch.object(s, "run_once", return_value=(0, "SCAN_OK")):
                self.assertEqual(s.main(["--worker", str(source)]), 0)
                self.assertEqual(json.loads((Path(td)/"status.json").read_text())["scans"], 1)

    def test_17_one_scan_failure(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "worker.py"; source.write_text("# worker")
            with patch.object(s, "check_worker", return_value=source), patch.object(s, "WORKER_SHA256", hashlib.sha256(source.read_bytes()).hexdigest()), patch.object(s, "STATE_DIR", Path(td)), patch.object(s, "run_once", return_value=(1, "ERROR")):
                self.assertEqual(s.main(["--worker", str(source)]), 1)

    def test_18_stop_after_five_errors(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "worker.py"; source.write_text("# worker")
            with patch.object(s, "check_worker", return_value=source), patch.object(s, "WORKER_SHA256", hashlib.sha256(source.read_bytes()).hexdigest()), patch.object(s, "STATE_DIR", Path(td)), patch.object(s, "run_once", return_value=(1, "ERROR")), patch.object(s.time, "sleep"):
                self.assertEqual(s.main(["--worker", str(source), "--poll"]), 5)
                self.assertEqual(json.loads((Path(td)/"status.json").read_text())["scans"], 5)

    def test_19_worker_tampered_mid_session(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "worker.py"; source.write_text("# worker")
            with patch.object(s, "check_worker", return_value=source), patch.object(s, "STATE_DIR", Path(td)), patch.object(s, "WORKER_SHA256", "0"*64), patch.object(s, "run_once") as runner:
                self.assertEqual(s.main(["--worker", str(source)]), 4)
                runner.assert_not_called()

    def test_20_worker_status_never_enables_production(self):
        with tempfile.TemporaryDirectory() as td:
            s.write_status(Path(td), state="HEALTHY")
            receipt = json.loads((Path(td) / "status.json").read_text())
            self.assertEqual(receipt["production"], "HOLD")


    def test_21_rejects_spoofed_success_marker(self):
        fake = types.SimpleNamespace(returncode=0, stdout="NOT_SCAN_DONE processed=1\\n".replace("\\n", "\n"), stderr="")
        with patch.object(s.subprocess, "run", return_value=fake):
            self.assertEqual(s.run_once(Path("/fake/worker.py")), (126, "SCAN_OUTPUT_UNKNOWN"))

    def test_22_rejects_invalid_scan_count(self):
        fake = types.SimpleNamespace(returncode=0, stdout="SCAN_DONE processed=bogus\\n".replace("\\n", "\n"), stderr="")
        with patch.object(s.subprocess, "run", return_value=fake):
            self.assertEqual(s.run_once(Path("/fake/worker.py")), (126, "SCAN_OUTPUT_UNKNOWN"))

    def test_23_rejects_trailing_unexpected_output(self):
        fake = types.SimpleNamespace(returncode=0, stdout="SCAN_DONE processed=1\\nUNEXPECTED\\n".replace("\\n", "\n"), stderr="")
        with patch.object(s.subprocess, "run", return_value=fake):
            self.assertEqual(s.run_once(Path("/fake/worker.py")), (126, "SCAN_OUTPUT_UNKNOWN"))

    def test_24_accepts_completed_scan_with_prior_lines(self):
        fake = types.SimpleNamespace(returncode=0, stdout="REPLIED job-20261025-02.json STATUS=PASS EXECUTED=False\\nSCAN_DONE processed=1\\n".replace("\\n", "\n"), stderr="")
        with patch.object(s.subprocess, "run", return_value=fake):
            self.assertEqual(s.run_once(Path("/fake/worker.py")), (0, "SCAN_OK"))

    def test_25_success_stdout_with_stderr_fails_closed(self):
        fake = types.SimpleNamespace(returncode=0, stdout="SCAN_DONE processed=1\n", stderr="unexpected warning")
        with patch.object(s.subprocess, "run", return_value=fake):
            self.assertEqual(s.run_once(Path("/fake/worker.py")), (126, "SCAN_STDERR_UNEXPECTED"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
