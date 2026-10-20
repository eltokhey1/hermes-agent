"""Real-source offline behavior tests for Hermes ESTOP and interrupt primitives.

Loads the exact checked-out Python modules under *dependency stubs* in temporary
directories. These are source-backed contract tests, not live Hermes runtime tests,
and do not activate an agent, gateway, terminal, or user machine.
"""
from __future__ import annotations

import importlib.util
import logging
import sys
import tempfile
import threading
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

REPO = Path(__file__).resolve().parents[3]
ESTOP = REPO / "agent" / "estop.py"
INTERRUPT = REPO / "tools" / "interrupt.py"


def _load_source(path: Path, name: str):
    if path.is_symlink() or bool(getattr(path, "is_junction", lambda: False)()):
        raise RuntimeError("LINKED_SOURCE_REFUSED")
    if not path.is_file() or not (0 < path.stat().st_size <= 512 * 1024):
        raise RuntimeError("SOURCE_UNAVAILABLE")
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError("MODULE_LOADER_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourceBackedESTOPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.profile = root / "profile"
        self.fleet = root / "fleet"
        self.profile.mkdir()
        self.fleet.mkdir()
        fake_agent = types.ModuleType("agent")
        fake_agent.__path__ = []
        fake_safety = types.ModuleType("agent.file_safety")
        fake_safety._hermes_home_path = lambda: self.profile
        fake_safety._hermes_root_path = lambda: self.fleet
        with patch.dict(sys.modules, {"agent": fake_agent, "agent.file_safety": fake_safety}):
            self.estop = _load_source(ESTOP, "hermes_source_estop_test")

    def test_off_by_default_in_isolated_home(self):
        self.assertFalse(self.estop.is_engaged())
        self.assertIsNone(self.estop.get_state())

    def test_engage_creates_real_marker_only_in_test_home(self):
        marker = self.estop.engage("unit test")
        self.assertEqual(marker, self.profile / "ESTOP")
        self.assertTrue(marker.is_file())
        self.assertTrue(self.estop.is_engaged())
        self.assertEqual(self.estop.get_state()["reason"], "unit test")

    def test_corrupt_marker_still_stops_new_work(self):
        (self.profile / "ESTOP").write_bytes(b"\x00nonsense")
        self.assertTrue(self.estop.is_engaged())
        self.assertTrue(self.estop.check_paused("scheduler", logging.getLogger("test")))
        self.assertIsNone(self.estop.get_state()["reason"])

    def test_fleet_marker_pauses_profile(self):
        (self.fleet / "ESTOP").touch()
        self.assertTrue(self.estop.is_engaged())

    def test_disengage_clears_both_test_markers(self):
        self.estop.engage()
        (self.fleet / "ESTOP").touch()
        self.assertTrue(self.estop.disengage())
        self.assertFalse(self.estop.is_engaged())

    def test_stat_errors_fail_safe(self):
        with patch.object(Path, "exists", side_effect=OSError("synthetic denied")):
            self.assertTrue(self.estop.is_engaged())

    def test_repeated_pause_logs_once_per_component(self):
        logger = Mock()
        self.estop.engage()
        self.assertTrue(self.estop.check_paused("scheduler", logger))
        self.assertTrue(self.estop.check_paused("scheduler", logger))
        self.assertEqual(logger.info.call_count, 1)

    def test_pause_is_not_a_thread_kill_switch(self):
        started = threading.Event()
        released = threading.Event()
        finished = threading.Event()
        def existing_work():
            started.set()
            released.wait(2)
            finished.set()
        worker = threading.Thread(target=existing_work)
        worker.start()
        try:
            self.assertTrue(started.wait(2))
            self.estop.engage()
            self.assertTrue(self.estop.is_engaged())
            self.assertTrue(worker.is_alive())
            released.set()
            self.assertTrue(finished.wait(2))
        finally:
            released.set()
            worker.join(timeout=2)
        self.assertFalse(worker.is_alive())


class SourceBackedInterruptTests(unittest.TestCase):
    def setUp(self):
        fake_utils = types.ModuleType("utils")
        fake_utils.env_var_enabled = lambda name: False
        with patch.dict(sys.modules, {"utils": fake_utils}):
            self.intr = _load_source(INTERRUPT, "hermes_source_interrupt_test")
        self.addCleanup(self.intr.set_interrupt, False)

    def test_interrupt_flag_applies_to_current_thread(self):
        self.intr.set_interrupt(True, reason="unit_test")
        self.assertTrue(self.intr.is_interrupted())
        self.intr.set_interrupt(False)
        self.assertFalse(self.intr.is_interrupted())

    def test_interrupted_thread_refuses_state_transition(self):
        called = []
        self.intr.set_interrupt(True)
        self.assertFalse(self.intr.run_if_not_interrupted(lambda: called.append("effect")))
        self.assertEqual(called, [])

    def test_clear_allows_noop_transition(self):
        called = []
        self.assertTrue(self.intr.run_if_not_interrupted(lambda: called.append("noop")))
        self.assertEqual(called, ["noop"])

    def test_interrupt_thread_scoping(self):
        set_flag = threading.Event()
        release = threading.Event()
        observed = []
        def worker():
            self.intr.set_interrupt(True)
            set_flag.set()
            release.wait(2)
            observed.append(self.intr.is_interrupted())
            self.intr.set_interrupt(False)
        t = threading.Thread(target=worker)
        t.start()
        try:
            self.assertTrue(set_flag.wait(2))
            self.assertFalse(self.intr.is_interrupted())
            release.set()
            t.join(timeout=2)
            self.assertEqual(observed, [True])
        finally:
            release.set()
            t.join(timeout=2)

    def test_context_delegation_respects_other_thread_interrupt(self):
        tid = threading.get_ident() + 999_999  # synthetic identity, not a real worker
        self.intr.set_interrupt(True, tid)
        token = self.intr.acting_for_tid.set(tid)
        try:
            self.assertTrue(self.intr.is_interrupted())
        finally:
            self.intr.acting_for_tid.reset(token)
            self.intr.set_interrupt(False, tid)

    def test_estop_module_and_interrupt_module_are_separate(self):
        # This is a deliberate non-acceptance assertion. Marker writes in
        # agent.estop do not automatically signal tools.interrupt.
        self.assertFalse(self.intr.is_interrupted())


if __name__ == "__main__":
    unittest.main()
