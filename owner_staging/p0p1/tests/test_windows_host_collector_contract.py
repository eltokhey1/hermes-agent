"""Regression checks for Windows host-readiness evidence boundaries.

Source-only assertions: passing does NOT verify the owner's actual Windows host.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "windows_p0_host_gate.ps1"


class WindowsHostCollectorBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")
        cls.flat = re.sub(r"\s+", " ", cls.source).lower()

    def test_absent_file_fails_closed(self):
        self.assertTrue(SCRIPT.is_file())
        self.assertIn("$erroractionpreference = 'stop'", self.flat)

    def test_never_claims_operational_acceptance(self):
        for key in ("G0='NO-GO'", "G_CODE='NO-GO'", "G1='NO-GO'", "production='HOLD'"):
            with self.subTest(key=key):
                self.assertIn(key.lower(), self.flat)

    def test_operational_proof_fields_remain_false(self):
        required = (
            "native_full_backup_verified",
            "functional_restore_verified",
            "estop_inflight_verified",
            "hermes_docker_runtime_isolation_verified",
            "estop_patch_integrated_on_host_verified",
            "independent_acceptance",
        )
        for name in required:
            with self.subTest(name=name):
                self.assertRegex(self.source, r"(?im)^\s*" + re.escape(name) + r"\s*=\s*\$false\b")

    def test_no_explicit_host_mutations(self):
        forbidden = (
            "set-acl", "takeown", "icacls", "remove-item", "move-item",
            "rename-item", "set-content", "add-content", "new-item",
            "start-process", "invoke-expression", "docker run",
            "docker compose up", "git reset", "git clean", "git checkout",
        )
        # Strip comments to focus this regression on executable source text.
        executable = "\n".join(
            line.split("#", 1)[0] for line in self.source.splitlines()
            if not line.lstrip().startswith("#")
        ).lower()
        for command in forbidden:
            with self.subTest(command=command):
                self.assertNotIn(command, executable)

    def test_partial_backups_are_not_full_restore(self):
        self.assertIn("LISTABLE_NOT_BACKED_UP", self.source)
        self.assertIn("ENGINE_REACHABLE_NOT_ISOLATION_PROOF", self.source)
        self.assertIn("MARKER_PRESENT_NEW_WORK_ONLY", self.source)


if __name__ == "__main__":
    unittest.main()
