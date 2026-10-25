"""Offline supervisor v2 safety gates; never invokes worker or GitHub."""
import contextlib
import io
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch
import test_supervisor_v2_integration as integration

s = integration.supervisor


class SupervisorV2SafetyGates(unittest.TestCase):
    def test_stops_after_five_consecutive_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            worker = pathlib.Path(tmp) / "worker.py"
            worker.write_text("# synthetic worker\n", encoding="utf-8")
            statuses = []
            def capture(path, **fields):
                statuses.append(fields)
            with patch.object(s, "check_worker", return_value=worker), \
                 patch.object(s, "STATE_DIR", pathlib.Path(tmp)), \
                 patch.object(s, "WORKER_SHA256", s.hashlib.sha256(worker.read_bytes()).hexdigest()), \
                 patch.object(s, "run_once", return_value=(1, "WORKER_EXIT_1")) as run, \
                 patch.object(s, "write_status", side_effect=capture), \
                 patch.object(s.time, "sleep"):
                code = s.main(["--worker", str(worker), "--poll", "--interval", "20"])
            self.assertEqual(code, 5)
            self.assertEqual(run.call_count, 5)
            self.assertEqual(statuses[-1]["state"], "STOPPED")
            self.assertEqual(statuses[-1]["consecutive_failures"], 5)

    def test_recovery_resets_failure_streak(self):
        with tempfile.TemporaryDirectory() as tmp:
            worker = pathlib.Path(tmp) / "worker.py"
            worker.write_text("# synthetic worker\n", encoding="utf-8")
            statuses = []
            scans = [(1, "WORKER_EXIT_1")] * 4 + [(0, "SCAN_OK")] + [(1, "WORKER_EXIT_1")] * 5
            with patch.object(s, "check_worker", return_value=worker), \
                 patch.object(s, "STATE_DIR", pathlib.Path(tmp)), \
                 patch.object(s, "WORKER_SHA256", s.hashlib.sha256(worker.read_bytes()).hexdigest()), \
                 patch.object(s, "run_once", side_effect=scans) as run, \
                 patch.object(s, "write_status", side_effect=lambda path, **kw: statuses.append(kw)), \
                 patch.object(s.time, "sleep"):
                code = s.main(["--worker", str(worker), "--poll", "--interval", "20"])
            self.assertEqual(code, 5)
            self.assertEqual(run.call_count, 10)
            self.assertEqual(statuses[4]["consecutive_failures"], 0)

    def test_invalid_interval_refused(self):
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(io.StringIO()):
            s.main(["--interval", "1"])
        self.assertEqual(cm.exception.code, 2)

    def test_rejects_modified_worker(self):
        with tempfile.TemporaryDirectory() as tmp:
            worker = pathlib.Path(tmp) / "worker.py"
            worker.write_text("# changed", encoding="utf-8")
            with patch.object(s, "WORKER_SHA256", "0" * 64):
                with self.assertRaises(ValueError):
                    s.check_worker(worker)

    @unittest.skipUnless(s.os.name == "nt", "Windows-only locking behavior")
    def test_windows_single_instance_lock(self):
        # This gate must be executed on Windows with a separate competing process.
        self.skipTest("Requires live two-process Windows acceptance; not simulated")


if __name__ == "__main__":
    unittest.main()
