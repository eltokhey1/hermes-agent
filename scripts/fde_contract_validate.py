"""Offline, fail-closed validator for proposed FDE delivery evidence receipts.

This utility does not run evidence commands, access credentials or approve releases.
It validates a receipt assembled by a human/reviewer; it does not prove claims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

_SHA256 = re.compile(r"[a-fA-F0-9]{64}\Z")
_COMMIT = re.compile(r"[a-fA-F0-9]{40}\Z")
_ARTIFACT_NAME = re.compile(r"[A-Za-z0-9._/-]{1,240}\Z")
_MAX_ARTIFACT_BYTES = 20 * 1024 * 1024
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


def _safe_artifact_path(value: Any) -> bool:
    """Require portable, relative paths below the evidence root."""
    return (
        isinstance(value, str)
        and bool(_ARTIFACT_NAME.fullmatch(value))
        and not PurePosixPath(value).is_absolute()
        and all(part not in {"", ".", ".."} for part in value.split("/"))
    )


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
            if not _safe_artifact_path(check.get("artifact_path")):
                errors.append(f"{prefix}.artifact_path must be a safe relative POSIX path for PASS")
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


def verify_artifacts(data: dict[str, Any], evidence_root: Path) -> list[str]:
    """Verify bounded, local SHA-256 digests without running recorded commands.

    The caller must first check validate_receipt(data) == []. This checks the
    bytes only; provenance and whether a command actually ran remain unproven.
    """
    try:
        if evidence_root.is_symlink() or not evidence_root.is_dir():
            return ["evidence root must be a real directory (not a symlink)"]
        root = evidence_root.resolve(strict=True)
    except (OSError, RuntimeError):
        return ["evidence root is not accessible"]
    errors: list[str] = []
    for check in data["checks"]:
        if check["status"] != "PASS":
            continue
        name = check["artifact_path"]
        label = f"artifact for {check['gate']}"
        target = root.joinpath(*PurePosixPath(name).parts)
        try:
            node = root
            for part in PurePosixPath(name).parts:
                node = node / part
                if node.is_symlink():
                    raise ValueError("symlink disallowed")
            resolved = target.resolve(strict=True)
            if not resolved.is_relative_to(root) or not target.is_file():
                raise ValueError("not a regular file within evidence root")
            if target.stat().st_size > _MAX_ARTIFACT_BYTES:
                raise ValueError("artifact exceeds 20 MiB cap")
            digest = hashlib.sha256()
            total = 0
            with target.open("rb") as stream:
                for block in iter(lambda: stream.read(64 * 1024), b""):
                    total += len(block)
                    if total > _MAX_ARTIFACT_BYTES:
                        raise ValueError("artifact exceeds 20 MiB cap")
                    digest.update(block)
            if digest.hexdigest().lower() != check["artifact_sha256"].lower():
                errors.append(f"{label}: SHA-256 mismatch")
        except (OSError, RuntimeError, ValueError) as exc:
            errors.append(f"{label}: {exc.__class__.__name__} while reading evidence")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="JSON receipt to validate, without executing commands")
    parser.add_argument("--evidence-root", type=Path, help="local root for actual offline artifact hash verification")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.receipt.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"INVALID RECEIPT: {exc.__class__.__name__}", file=sys.stderr)
        return 2
    errors = validate_receipt(data)
    if not errors:
        if args.evidence_root is None:
            errors.append("PASS claims require --evidence-root for offline artifact verification")
        else:
            errors.extend(verify_artifacts(data, args.evidence_root))
    if errors:
        for msg in errors:
            print(f"FAIL: {msg}")
        print("VERDICT=NOT_READY")
        return 1
    print("VERDICT=ARTIFACT_HASHES_MATCH; HUMAN_REVIEW_REQUIRED; PRODUCTION_APPROVED=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
