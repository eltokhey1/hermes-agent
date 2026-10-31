#!/usr/bin/env python3
"""Offline, stdlib-only, SYNTHETIC comparison of document parser field outputs.

This script does not run a parser, use real trade documents, authorize adoption,
write data, call a provider, or claim Windows-native testing. Output has counts
and input hash only; original BL/LC field values are never printed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

MAX_INPUT_BYTES = 128 * 1024
MAX_CASES = 50
NAME_RE = re.compile(r"[a-z][a-z0-9_]{0,47}\Z")
CASE_RE = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")


class InputError(ValueError):
    """Invalid or unsafe benchmark input."""


def _keys(value: object, required: set[str], where: str) -> dict:
    if not isinstance(value, dict) or set(value) != required:
        raise InputError(f"{where}: unexpected or missing keys")
    return value


def _fields(value: object, where: str, *, nonempty: bool) -> dict[str, str]:
    if not isinstance(value, dict) or len(value) > 40 or (nonempty and not value):
        raise InputError(f"{where}: invalid field map")
    for key, item in value.items():
        if not isinstance(key, str) or not NAME_RE.fullmatch(key):
            raise InputError(f"{where}: invalid field name")
        if not isinstance(item, str) or len(item) > 512 or (nonempty and not item.strip()):
            raise InputError(f"{where}: field values must be bounded nonempty strings")
    return value


def _score(cases: list[dict], method: str) -> dict[str, int]:
    score = {"correct": 0, "missing": 0, "incorrect": 0, "critical_errors": 0, "extra": 0}
    for case in cases:
        expected = case["expected"]
        actual = case[method]
        score["extra"] += len(actual.keys() - expected.keys())
        for field, target in expected.items():
            prediction = actual.get(field)
            if prediction is None:
                score["missing"] += 1
            elif " ".join(prediction.split()) == " ".join(target.split()):
                score["correct"] += 1
                continue
            else:
                score["incorrect"] += 1
            if field in case["critical"]:
                score["critical_errors"] += 1
    return score


def evaluate(data: object) -> dict:
    obj = _keys(data, {"schema", "synthetic", "baseline_name", "challenger_name", "cases"}, "root")
    if obj["schema"] != "hermes_parser_challenger_v1" or obj["synthetic"] is not True:
        raise InputError("synthetic=true and recognized schema required")
    for label in ("baseline_name", "challenger_name"):
        if not isinstance(obj[label], str) or not CASE_RE.fullmatch(obj[label]):
            raise InputError(f"{label}: invalid identifier")
    if obj["baseline_name"] == obj["challenger_name"]:
        raise InputError("baseline and challenger must have different identifiers")
    cases = obj["cases"]
    if not isinstance(cases, list) or not 1 <= len(cases) <= MAX_CASES:
        raise InputError("cases must contain 1..50 synthetic records")
    seen = set()
    total_fields = 0
    for index, raw in enumerate(cases):
        case = _keys(raw, {"id", "expected", "critical", "baseline", "challenger"}, f"case {index}")
        cid = case["id"]
        if not isinstance(cid, str) or not CASE_RE.fullmatch(cid) or cid in seen:
            raise InputError("case IDs must be unique safe identifiers")
        seen.add(cid)
        target = _fields(case["expected"], f"case {index}.expected", nonempty=True)
        _fields(case["baseline"], f"case {index}.baseline", nonempty=False)
        _fields(case["challenger"], f"case {index}.challenger", nonempty=False)
        critical = case["critical"]
        if (not isinstance(critical, list) or not critical or len(set(map(str, critical))) != len(critical)
                or any(not isinstance(k, str) or k not in target for k in critical)):
            raise InputError(f"case {index}: invalid critical field list")
        total_fields += len(target)
    base, candidate = _score(cases, "baseline"), _score(cases, "challenger")
    promising = (candidate["correct"] > base["correct"]
                 and candidate["critical_errors"] == 0
                 and candidate["extra"] <= base["extra"])
    return {
        "schema": "hermes_parser_challenger_result_v1",
        "evidence": "TESTED_SYNTHETIC_ONLY",
        "production": "HOLD",
        "real_tools_executed": False,
        "native_windows_evidence": "NOT_VERIFIED",
        "latency_ram_cost": "NOT_MEASURED",
        "case_count": len(cases),
        "expected_fields": total_fields,
        "baseline": {"name": obj["baseline_name"], **base},
        "challenger": {"name": obj["challenger_name"], **candidate},
        "decision": "CANDIDATE_FOR_APPROVED_NATIVE_TEST" if promising else "RETAIN_BASELINE",
        "tool_promotion_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path, help="explicit synthetic JSON comparison fixture")
    args = parser.parse_args(argv)
    try:
        path = args.fixture
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_INPUT_BYTES:
            raise InputError("fixture must be a regular non-symlink file <=128 KiB")
        raw = path.read_bytes()
        if len(raw) > MAX_INPUT_BYTES:
            raise InputError("fixture exceeds 128 KiB")
        report = evaluate(json.loads(raw.decode("utf-8")))
        report["fixture_sha256"] = hashlib.sha256(raw).hexdigest()
    except (OSError, UnicodeError, json.JSONDecodeError, InputError):
        print(json.dumps({"error": "INVALID_FIXTURE", "decision": "INVALID_INPUT", "production": "HOLD"}))
        return 2
    print(json.dumps(report, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
