"""Offline, fail-closed validator for proposed FDE delivery evidence receipts.

This utility does not run evidence commands, access credentials or approve releases.
It validates a receipt assembled by a human/reviewer; it does not prove claims.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_SHA256 = re.compile(r"[a-fA-F0-9]{64}\Z")
_COMMIT = re.compile(r"[a-fA-F0-9]{40}\Z")
_CHECK_STATUSES = {"PASS", "FAIL", "UNKNOWN"}
_REQUIRED_GATES = {"security", "recovery", "idempotency", "privacy", "quality"}


def _timezoned(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None and parsed.utcoffset() is not None
    except ValueError:
        return False


def validate_receipt(data: Any) -> list[str]:
    """Return actionable violations; an empty list means evidence-shaped, NOT safe to deploy."""
    if not isinstance(data, dict):
        return ["receipt must be an object"]
    errors: list[str] = []

    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        errors.append("schema_version must be 1")
    for field in ("project_id", "scope"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            errors.append(f"{field} must be a nonempty string")
    if not isinstance(data.get("base_commit"), str) or not _COMMIT.fullmatch(data["base_commit"]):
        errors.append("base_commit must be a 40-character git commit SHA")
    if not isinstance(data.get("environment"), str) or data["environment"] not in {"sandbox", "staging", "production"}:
        errors.append("environment must be sandbox, staging, or production")
    if not _timezoned(data.get("observed_at")):
        errors.append("observed_at must be an ISO-8601 timestamp with timezone")

    release = data.get("release")
    if not isinstance(release, dict):
        errors.append("release must be an object")
    else:
        if release.get("intent") != "review_only":
            errors.append("release.intent must be review_only (this validator cannot approve deployments)")
        if release.get("production_approved") is not False:
            errors.append("release.production_approved must be false")

    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        errors.append("checks must be a nonempty array")
        return errors
    seen: set[str] = set()
    for index, check in enumerate(checks):
        prefix = f"checks[{index}]"
        if not isinstance(check, dict):
            errors.append(f"{prefix} must be an object")
            continue
        gate = check.get("gate")
        if not isinstance(gate, str) or not gate.strip():
            errors.append(f"{prefix}.gate must be a nonempty string")
        elif gate in seen:
            errors.append(f"{prefix}.gate is duplicated: {gate}")
        else:
            seen.add(gate)
        status = check.get("status")
        if not isinstance(status, str) or status not in _CHECK_STATUSES:
            errors.append(f"{prefix}.status must be PASS, FAIL, or UNKNOWN")
        if not isinstance(check.get("description"), str) or not check["description"].strip():
            errors.append(f"{prefix}.description must be nonempty")
        if status == "PASS":
            if not isinstance(check.get("command"), str) or not check["command"].strip():
                errors.append(f"{prefix}.command required for PASS")
            if type(check.get("exit_code")) is not int or check["exit_code"] != 0:
                errors.append(f"{prefix}.exit_code must be integer 0 for PASS")
            digest = check.get("artifact_sha256")
            if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
                errors.append(f"{prefix}.artifact_sha256 must be a SHA-256 hex digest for PASS")
            if not _timezoned(check.get("observed_at")):
                errors.append(f"{prefix}.observed_at timezone required for PASS")
        if status != "PASS" and (check.get("exit_code") == 0 and type(check.get("exit_code")) is int):
            errors.append(f"{prefix} non-PASS must not claim successful exit_code 0")

    missing = sorted(_REQUIRED_GATES - seen)
    if missing:
        errors.append("missing required gates: " + ", ".join(missing))
    for gate in sorted(_REQUIRED_GATES & seen):
        for check in checks:
            if isinstance(check, dict) and check.get("gate") == gate and check.get("status") != "PASS":
                errors.append(f"required gate not PASS: {gate}")
                break
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="JSON receipt to validate, without executing commands")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.receipt.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"INVALID RECEIPT: {exc.__class__.__name__}", file=sys.stderr)
        return 2
    errors = validate_receipt(data)
    if errors:
        for msg in errors:
            print(f"FAIL: {msg}")
        print("VERDICT=NOT_READY")
        return 1
    print("VERDICT=EVIDENCE_SHAPE_VALID; HUMAN_REVIEW_REQUIRED; PRODUCTION_APPROVED=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
