"""Source-backed ESTOP pause/resume failure tests in isolated temporary homes only.

The tested code comes from branch-local Hermes modules, not reimplemented mocks.
External Hermes dependencies are stubbed; tests never reach the user's host.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
ESTOP_PATH = ROOT / "agent" / "estop.py"
CLI_PATH = ROOT / "hermes_cli" / "subcommands" / "pause.py"


def load(path: Path, name: str):
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("SOURCE_NOT_REGULAR")
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError("SOURCE_LOADER_MISSING")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PauseCliFailClosedTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.profile = root / "profile"
        self.fleet = root / "fleet"
        self.profile.mkdir()
        self.fleet.mkdir()
        fake_agent = types.ModuleType("agent")
        fake_agent.__path__ = []
        fake_fs = types.ModuleType("agent.file_safety")
        fake_fs._hermes_home_path = lambda: self.profile
        fake_fs._hermes_root_path = lambda: self.fleet
        with patch.dict(sys.modules, {"agent":fake_agent, "agent.file_safety":fake_fs}):
            self.estop = load(ESTOP_PATH, "p0_real_estop_cli_test")
        self.cli = load(CLI_PATH, "p0_real_pause_cli_test")
        self.real_module_dict = {"agent.estop": self.estop}

    def call_pause(self):
        output = io.StringIO()
        with patch.dict(sys.modules, self.real_module_dict):
            with contextlib.redirect_stdout(output):
                result = self.cli.cmd_pause(argparse.Namespace(reason="isolated unit test"))
        return result, output.getvalue()

    def call_resume(self):
        output = io.StringIO()
        with patch.dict(sys.modules, self.real_module_dict):
            with contextlib.redirect_stdout(output):
                result = self.cli.cmd_resume(argparse.Namespace())
        return result, output.getvalue()

    def test_pause_success_creates_marker(self):
        rc, output = self.call_pause()
        self.assertEqual(rc, 0)
        self.assertTrue((self.profile / "ESTOP").is_file())
        self.assertIn("paused", output)

    def test_pause_idempotent_existing_marker(self):
        self.assertEqual(self.call_pause()[0], 0)
        rc, out = self.call_pause()
        self.assertEqual(rc, 0)
        self.assertIn("Still paused", out)

    def test_pause_full_write_denial_is_nonzero(self):
        with patch.object(Path, "write_text", side_effect=PermissionError("synthetic write denied")):
            with patch.object(Path, "touch", side_effect=PermissionError("synthetic touch denied")):
                rc, output = self.call_pause()
        self.assertEqual(rc, 2)
        self.assertIn("NOT verified", output)
        self.assertNotIn("Hermes paused", output)

    def test_pause_fallback_touch_succeeds(self):
        with patch.object(Path, "write_text", side_effect=PermissionError("synthetic text denied")):
            rc, output = self.call_pause()
        self.assertEqual(rc, 0)
        self.assertTrue((self.profile / "ESTOP").is_file())
        self.assertIn("paused", output)

    def test_pause_stat_denial_is_nonzero(self):
        # Marker contents may exist, but operator cannot verify durable state.
        with patch.object(Path, "stat", side_effect=PermissionError("synthetic stat denied")):
            rc, output = self.call_pause()
        self.assertEqual(rc, 2)
        self.assertIn("NOT verified", output)

    def test_resume_with_no_marker_is_nondestructive(self):
        rc, out = self.call_resume()
        self.assertEqual(rc, 0)
        self.assertIn("not paused", out)

    def test_resume_clears_both_markers(self):
        self.estop.engage()
        (self.fleet / "ESTOP").touch()
        rc, out = self.call_resume()
        self.assertEqual(rc, 0)
        self.assertIn("resumed", out)
        self.assertFalse((self.profile / "ESTOP").exists())
        self.assertFalse((self.fleet / "ESTOP").exists())

    def test_resume_unlink_denied_is_nonzero(self):
        self.estop.engage()
        with patch.object(Path, "unlink", side_effect=PermissionError("synthetic unlink denied")):
            rc, out = self.call_resume()
        self.assertEqual(rc, 2)
        self.assertIn("NOT verified", out)
        self.assertNotIn("resumed", out)

    def test_resume_fleet_marker_unlink_denied_is_nonzero(self):
        self.estop.engage()
        (self.fleet / "ESTOP").touch()
        native_unlink = Path.unlink
        def deny_only_fleet(path, *args, **kw):
            if path == self.fleet / "ESTOP":
                raise PermissionError("synthetic fleet denied")
            return native_unlink(path, *args, **kw)
        with patch.object(Path, "unlink", deny_only_fleet):
            rc, out = self.call_resume()
        self.assertEqual(rc, 2)
        self.assertIn("NOT verified", out)
        self.assertTrue((self.fleet / "ESTOP").is_file())

    def test_unresolvable_fleet_root_engages_estop(self):
        with patch.object(self.estop, "_canonical_root", side_effect=PermissionError("synthetic root denied")):
            self.assertTrue(self.estop.is_engaged())

    def test_unresolvable_fleet_root_has_unknown_paused_state(self):
        with patch.object(self.estop, "_canonical_root", side_effect=PermissionError("synthetic root denied")):
            self.assertEqual(self.estop.get_state(), {"reason": None, "engaged_at": None})
            self.assertIn("paused", self.estop.paused_reply())

    def test_resume_fails_when_fleet_root_is_unverifiable(self):
        with patch.object(self.estop, "_canonical_root", side_effect=PermissionError("synthetic root denied")):
            rc, out = self.call_resume()
        self.assertEqual(rc, 2)
        self.assertIn("NOT verified", out)
        self.assertNotIn("Hermes resumed", out)

    def test_resume_stat_denial_is_nonzero(self):
        self.estop.engage()
        with patch.object(Path, "stat", side_effect=PermissionError("synthetic stat denied")):
            rc, out = self.call_resume()
        self.assertEqual(rc, 2)
        self.assertIn("NOT verified", out)

    def test_paused_reply_discloses_new_work_only(self):
        self.estop.engage()
        reply = self.estop.paused_reply()
        self.assertIn("New work is on hold", reply)

    def test_cannot_claim_inflight_cancellation(self):
        self.assertIn("in-flight work is never killed", ESTOP_PATH.read_text(encoding="utf-8"))
        self.assertIn("In-flight work keeps running", CLI_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
