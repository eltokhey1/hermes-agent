"""Offline deterministic acceptance tests: no GitHub/network/untrusted execution."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch, MagicMock
import sys

import guarded_supervisor_launcher_v1 as g


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.start = dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1)

    def status(self, **overrides):
        info = {"schema": "hermes.bridge.supervisor.status.v1",
                "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "state": "HEALTHY", "last_scan": "SCAN_OK", "last_exit_code": 0,
                "consecutive_failures": 0, "polling": True, "production": "HOLD",
                "worker_sha256": g.WORKER_SHA256}
        info.update(overrides)
        (self.root / "status.json").write_text(json.dumps(info), encoding="utf-8")
        return self.root / "status.json"

    def test_01_fresh_success(self):
        self.assertTrue(g.healthy_status(self.status(), self.start))

    def test_02_stale_status_is_not_success(self):
        old = (self.start - dt.timedelta(seconds=120)).isoformat()
        self.assertFalse(g.healthy_status(self.status(timestamp_utc=old), self.start))

    def test_03_degraded_and_nonzero_not_success(self):
        self.assertFalse(g.healthy_status(self.status(state="DEGRADED", last_exit_code=1), self.start))

    def test_04_production_must_be_hold(self):
        self.assertFalse(g.healthy_status(self.status(production="ON"), self.start))

    def test_05_wrong_worker_hash_rejected(self):
        self.assertFalse(g.healthy_status(self.status(worker_sha256="0"*64), self.start))

    def test_06_nonpolling_not_ready(self):
        self.assertFalse(g.healthy_status(self.status(polling=False), self.start))

    def test_07_malformed_json_not_ready(self):
        p = self.root / "status.json"; p.write_text("{bad")
        self.assertFalse(g.healthy_status(p, self.start))

    def test_08_missing_status_not_ready(self):
        self.assertFalse(g.healthy_status(self.root / "missing.json", self.start))

    def test_09_early_exit_rejected(self):
        self.status()
        process = types.SimpleNamespace(poll=lambda: 1)
        self.assertEqual(g.wait_ready(process, self.root / "status.json", self.start), "SUPERVISOR_EXITED_EARLY")

    def test_10_live_child_fresh_status_ready(self):
        self.status()
        process = types.SimpleNamespace(poll=lambda: None)
        self.assertEqual(g.wait_ready(process, self.root / "status.json", self.start), "READY")

    def test_11_live_child_stale_status_times_out(self):
        self.status(timestamp_utc=(self.start - dt.timedelta(minutes=1)).isoformat())
        process = types.SimpleNamespace(poll=lambda: None)
        with patch.object(g.time, "sleep", return_value=None):
            self.assertEqual(g.wait_ready(process, self.root / "status.json", self.start,
                                          timeout=0.01, interval=0), "STARTUP_TIMEOUT")

    def test_12_pinned_hash(self):
        p = self.root / "worker.py"; p.write_bytes(b"# trusted test fixture\n")
        self.assertEqual(g.check_pin(p, hashlib.sha256(p.read_bytes()).hexdigest()), p.resolve())
        with self.assertRaisesRegex(ValueError, "PINNED_HASH_MISMATCH"):
            g.check_pin(p, "0"*64)

    def test_13_future_timestamp_rejected(self):
        future = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=1)).isoformat()
        self.assertFalse(g.healthy_status(self.status(timestamp_utc=future), self.start))

    def test_14_no_success_from_wrong_schema(self):
        self.assertFalse(g.healthy_status(self.status(schema="other"), self.start))

    def test_15_missing_fields_not_success(self):
        p = self.root / "status.json"
        p.write_text('{"state":"HEALTHY"}', encoding="utf-8")
        self.assertFalse(g.healthy_status(p, self.start))

    def test_16_file_too_large_rejected(self):
        p = self.root / "worker.py"; p.write_bytes(b"x" * 100_001)
        with self.assertRaisesRegex(ValueError, "PINNED_FILE_INVALID"):
            g.check_pin(p, hashlib.sha256(p.read_bytes()).hexdigest())

    def test_17_refuse_false_exit_code_boolean(self):
        self.assertFalse(g.healthy_status(self.status(last_exit_code=False), self.start))

    def test_18_refuse_malformed_timestamp(self):
        self.assertFalse(g.healthy_status(self.status(timestamp_utc="not-a-date"), self.start))

    def test_19_refuse_naive_timestamp(self):
        self.assertFalse(g.healthy_status(self.status(timestamp_utc="2026-10-26T12:00:00"), self.start))

    def test_20_refuse_oversize_status(self):
        p = self.root / "status.json"; p.write_bytes(b"x" * 8193)
        self.assertFalse(g.healthy_status(p, self.start))

    def test_21_refuse_unpinned_worker_before_spawn(self):
        with patch.object(g.subprocess, "Popen") as spawn:
            self.assertEqual(g.main(["--folder", str(self.root), "--python", sys.executable]), 2)
            spawn.assert_not_called()

    def test_22_launch_success_requires_ready(self):
        worker = self.root / "hermes_bridge_v1.py"; worker.write_bytes(b"# trusted worker fixture\n")
        supervisor = self.root / "hermes_bridge_supervisor_v1.py"; supervisor.write_bytes(b"# trusted supervisor fixture\n")
        fake = MagicMock(); fake.poll.return_value = None
        with patch.object(g, "WORKER_SHA256", hashlib.sha256(worker.read_bytes()).hexdigest()), \
             patch.object(g, "SUPERVISOR_SHA256", hashlib.sha256(supervisor.read_bytes()).hexdigest()), \
             patch.object(g.subprocess, "Popen", return_value=fake) as spawn, \
             patch.object(g, "wait_ready", return_value="READY"):
            self.assertEqual(g.main(["--folder", str(self.root), "--python", sys.executable]), 0)
            self.assertEqual(spawn.call_count, 1)
            argv = spawn.call_args.args[0]
            self.assertEqual(argv[1:4], ["-I", "-B", "-S"])
            self.assertIn("--poll", argv)
            self.assertEqual(argv[-2:], ["--interval", "30"])
            self.assertNotIn("aider", " ".join(argv).lower())
            self.assertNotIn("shell", spawn.call_args.kwargs)
            fake.terminate.assert_not_called()

    def test_23_timeout_terminates_own_child(self):
        worker = self.root / "hermes_bridge_v1.py"; worker.write_bytes(b"# trusted worker fixture\n")
        supervisor = self.root / "hermes_bridge_supervisor_v1.py"; supervisor.write_bytes(b"# trusted supervisor fixture\n")
        fake = MagicMock(); fake.poll.return_value = None
        with patch.object(g, "WORKER_SHA256", hashlib.sha256(worker.read_bytes()).hexdigest()), \
             patch.object(g, "SUPERVISOR_SHA256", hashlib.sha256(supervisor.read_bytes()).hexdigest()), \
             patch.object(g.subprocess, "Popen", return_value=fake), \
             patch.object(g, "wait_ready", return_value="STARTUP_TIMEOUT"):
            self.assertEqual(g.main(["--folder", str(self.root), "--python", sys.executable]), 1)
            fake.terminate.assert_called_once()
            fake.wait.assert_called_once_with(timeout=3)

    def test_24_immediate_exit_does_not_terminate_other_process(self):
        worker = self.root / "hermes_bridge_v1.py"; worker.write_bytes(b"# trusted worker fixture\n")
        supervisor = self.root / "hermes_bridge_supervisor_v1.py"; supervisor.write_bytes(b"# trusted supervisor fixture\n")
        fake = MagicMock(); fake.poll.return_value = 3
        with patch.object(g, "WORKER_SHA256", hashlib.sha256(worker.read_bytes()).hexdigest()), \
             patch.object(g, "SUPERVISOR_SHA256", hashlib.sha256(supervisor.read_bytes()).hexdigest()), \
             patch.object(g.subprocess, "Popen", return_value=fake), \
             patch.object(g, "wait_ready", return_value="SUPERVISOR_EXITED_EARLY"):
            self.assertEqual(g.main(["--folder", str(self.root), "--python", sys.executable]), 1)
            fake.terminate.assert_not_called()

    def test_25_refuse_invalid_timeout(self):
        with self.assertRaises(SystemExit) as cm:
            g.main(["--folder", str(self.root), "--timeout", "999"])
        self.assertEqual(cm.exception.code, 2)

if __name__ == "__main__":
    unittest.main(verbosity=2)
