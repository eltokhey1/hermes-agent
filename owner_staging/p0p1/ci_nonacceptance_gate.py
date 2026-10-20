"""P0/P1 OFFLINE CI guard: fail closed on source-contract drift; never authorizes Hermes.

This is a static source review of tracked repository files. It does not execute
Hermes, cancel tasks, verify Docker runtime settings, or accept production.
"""
from __future__ import annotations

import argparse
import json
import re
import unittest
from pathlib import Path

from source_contract_audit import audit_source_tree

SOURCE_NAMES = ("estop", "docker", "terminal_backends")
REQUIRED_FLAGS = frozenset({
    "DISPATCH_ENFORCEMENT_UNVERIFIED",
    "ACTIVE_WORK_TERMINATION_UNVERIFIED",
    "WINDOWS_RUNTIME_UNVERIFIED",
    "INDEPENDENT_REVIEW_REQUIRED",
    "ESTOP_STATED_NEW_WORK_ONLY_NOT_KILL_SWITCH",
    "DOCKER_BASE_CAPABILITY_ADDITIONS_REQUIRE_REVIEW",
    "DOCKER_NETWORK_DEFAULT_NOT_PROVEN_OFF",
    "DOCKER_PERSISTENCE_DEFAULT_NOT_PROVEN_OFF",
    "CROSS_PROCESS_REUSE_DEFAULT_NOT_PROVEN_OFF",
})
# These are *reviewed source properties*, NOT secure production settings.
# Any change requires a human review and a corresponding evidence update.
REVIEWED_PROPERTIES = {
    "estop_entrypoints_declared": True,
    "estop_new_work_only_documented": True,
    "docker_capabilities_added_by_base_policy": True,
    "docker_no_new_privileges_flag_declared": True,
    "docker_default_network": True,
    "docker_default_persistence": True,
    "docker_default_cross_process_persistence": True,
}
_HEX = re.compile(r"^[a-f0-9]{64}$")


def validate_report(report: object) -> list[str]:
    """Return stable error codes, never values, source contents, or secrets."""
    failures: list[str] = []
    if not isinstance(report, dict):
        return ["INVALID_REPORT"]
    if report.get("scope") != "OFFLINE_STATIC_SOURCE_REVIEW_NOT_RUNTIME_ACCEPTANCE":
        failures.append("INVALID_SCOPE")
    sources = report.get("sources")
    if not isinstance(sources, dict):
        failures.append("MISSING_SOURCES")
    else:
        for name in SOURCE_NAMES:
            rec = sources.get(name)
            if not isinstance(rec, dict) or rec.get("status") != "PARSED":
                failures.append("SOURCE_NOT_PARSED:" + name)
            elif not isinstance(rec.get("sha256"), str) or not _HEX.fullmatch(rec["sha256"]):
                failures.append("SOURCE_NOT_PINNED:" + name)
    props = report.get("review_signals")
    if not isinstance(props, dict):
        failures.append("MISSING_SIGNALS")
    else:
        for key, value in REVIEWED_PROPERTIES.items():
            if props.get(key) is not value:
                failures.append("SOURCE_CONTRACT_DRIFT:" + key)
    flags = report.get("risk_flags")
    if not isinstance(flags, list) or not all(isinstance(v, str) for v in flags):
        failures.append("MALFORMED_RISK_FLAGS")
    else:
        failures.extend("RISK_FLAG_MISSING:" + flag for flag in sorted(REQUIRED_FLAGS - set(flags)))
    for key, value in (("assessment", "HOLD"), ("production", "HOLD"),
                       ("G0", "NO-GO"), ("G_CODE", "NO-GO"), ("G1", "NO-GO")):
        if report.get(key) != value:
            failures.append("INVALID_GATE:" + key)
    return sorted(set(failures))


def discover_tests(test_dir: Path, required_minimum: int) -> int:
    """Detect missing test modules before running; test execution is a separate CI step."""
    if required_minimum < 154:
        raise ValueError("test floor cannot be lowered below 154")
    if not test_dir.is_dir() or test_dir.is_symlink():
        raise ValueError("test tree missing or linked")
    # The global defaultTestLoader remembers the previous discovery root.
    # A fresh loader plus an explicit top-level avoids cross-fixture pollution
    # on Python 3.12 (Linux) and separate module-cache collisions on Windows.
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern="test_*.py", top_level_dir=str(test_dir))
    count = suite.countTestCases()
    if count < required_minimum:
        raise ValueError("test discovery below pinned minimum")
    return count


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="OFFLINE source drift checks; NEVER production acceptance")
    p.add_argument("--source-root", type=Path, required=True)
    p.add_argument("--min-tests", type=int, default=154)
    args = p.parse_args(argv)
    errors: list[str] = []
    discovered: int | None = None
    try:
        discovered = discover_tests(args.source_root / "owner_staging/p0p1/tests", args.min_tests)
    except (ValueError, OSError, ImportError, SyntaxError) as ex:
        errors.append("TEST_DISCOVERY_FAILED:" + type(ex).__name__)
    try:
        errors.extend(validate_report(audit_source_tree(args.source_root)))
    except (OSError, ValueError, TypeError, RecursionError) as ex:
        errors.append("SOURCE_AUDIT_FAILED:" + type(ex).__name__)
    print(json.dumps({
        "status": "OFFLINE_SOURCE_CONTRACT_PASS_NON_ACCEPTANCE" if not errors else "SAFE_STOP",
        "discovered_tests": discovered,
        "errors": sorted(set(errors)),
        "host_verified": False,
        "estop_inflight_verified": False,
        "runtime_isolation_verified": False,
        "G0": "NO-GO", "G_CODE": "NO-GO", "G1": "NO-GO",
        "production": "HOLD",
    }, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
