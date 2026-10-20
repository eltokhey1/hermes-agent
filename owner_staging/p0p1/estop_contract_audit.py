"""Non-executing ESTOP source-contract audit for Hermes P0.

This is a static source-inspection aid, never a safety or production acceptance.
Only reads nominated Python source files; does not import Hermes, read config/env,
run an agent, create an ESTOP marker, change permissions or contact services.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import re
from pathlib import Path

MAX_SOURCE_BYTES = 512 * 1024
KNOWN_CLI_STOP_SCOPE = "NEW_WORK_ONLY"


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _method_call(tree: ast.AST, method: str) -> bool:
    return any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
               and node.func.attr == method for node in ast.walk(tree))


def _name_call(tree: ast.AST, name: str) -> bool:
    return any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
               and node.func.id == name for node in ast.walk(tree))


def _functions(tree: ast.AST) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    return {node.name: node for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _sentinel_literal(tree: ast.AST) -> bool:
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SENTINEL_NAME" for t in node.targets):
            if isinstance(node.value, ast.Constant) and node.value.value == "ESTOP":
                return True
    return False


def _stat_error_fail_safe(function: ast.AST) -> bool:
    has_oserror_guard = False
    for node in ast.walk(function):
        if not isinstance(node, ast.ExceptHandler):
            continue
        ex = node.type
        if isinstance(ex, ast.Name) and ex.id == "OSError":
            has_oserror_guard = True
        if isinstance(ex, ast.Tuple) and any(isinstance(e, ast.Name) and e.id == "OSError" for e in ex.elts):
            has_oserror_guard = True
    # Evidence only: the documented code returns saw_stat_error; this is NOT a formal proof.
    returns_error_flag = any(isinstance(node, ast.Return) and isinstance(node.value, ast.Name)
                             and node.value.id == "saw_stat_error" for node in ast.walk(function))
    return has_oserror_guard and returns_error_flag


def _read_source(path: Path, expected_blob: str | None) -> tuple[str, dict]:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        raise ValueError("LINKED_SOURCE_REFUSED")
    if not path.is_file():
        raise ValueError("SOURCE_NOT_REGULAR_FILE")
    size = path.stat().st_size
    if size == 0 or size > MAX_SOURCE_BYTES:
        raise ValueError("SOURCE_SIZE_OUT_OF_BOUNDS")
    data = path.read_bytes()
    if len(data) != size:
        raise ValueError("SOURCE_SIZE_CHANGED_DURING_READ")
    digest = git_blob_sha1(data)
    if expected_blob and (not re.fullmatch(r"[0-9a-f]{40}", expected_blob) or digest != expected_blob):
        raise ValueError("GIT_BLOB_SHA_MISMATCH")
    return data.decode("utf-8"), {"git_blob_sha1": digest, "pinned": bool(expected_blob)}


def inspect_estop_source(source: str, pause_cli_source: str | None = None) -> dict:
    try:
        tree = ast.parse(source)
        cli_tree = ast.parse(pause_cli_source) if pause_cli_source is not None else None
    except SyntaxError:
        return {"status": "INVALID_SOURCE", "checks": {}, "blocking_findings": ["SOURCE_SYNTAX_ERROR"],
                "hard_cancel_verified": False, "tool_dispatch_verified": False, "production": "HOLD"}
    funcs = _functions(tree)
    engage = funcs.get("engage")
    disengage = funcs.get("disengage")
    engaged = funcs.get("is_engaged")
    check = funcs.get("check_paused")
    cli_funcs = _functions(cli_tree) if cli_tree is not None else {}
    checks = {
        "sentinel_name_literal_estop": _sentinel_literal(tree),
        "engage_writes_marker": engage is not None and (_method_call(engage, "write_text") or _method_call(engage, "touch")),
        "resume_removes_marker": disengage is not None and _method_call(disengage, "unlink"),
        "check_paused_queries_state": check is not None and _name_call(check, "is_engaged"),
        "stat_error_guard_observed": engaged is not None and _stat_error_fail_safe(engaged),
        "pause_cli_engages": cli_tree is not None and cli_funcs.get("cmd_pause") is not None
                             and _name_call(cli_funcs["cmd_pause"], "engage"),
        "resume_cli_disengages": cli_tree is not None and cli_funcs.get("cmd_resume") is not None
                              and _name_call(cli_funcs["cmd_resume"], "disengage"),
    }
    blockers = ["MISSING_SOURCE_CONTRACT:" + k for k, v in checks.items() if not v]
    doc = ast.get_docstring(tree) or ""
    pause_doc = ast.get_docstring(cli_tree) if cli_tree is not None else ""
    new_only = bool(re.search(r"(?:new work only|in-flight work is never killed)", doc, re.I)
                    or re.search(r"in-flight work keeps running", pause_cli_source or "", re.I))
    if new_only:
        blockers.append("IN_FLIGHT_WORK_NOT_CANCELLED_BY_ESTOP")
    else:
        blockers.append("IN_FLIGHT_CANCELLATION_UNVERIFIED")
    blockers += ["NO_TOOL_DISPATCH_ENFORCEMENT_TEST", "NO_WINDOWS_ESTOP_ACCEPTANCE_TEST"]
    return {
        "status": "STATIC_SOURCE_REVIEW_ONLY" if all(checks.values()) else "SOURCE_CONTRACT_INCOMPLETE",
        "checks": checks,
        "checks_passed": sum(bool(x) for x in checks.values()),
        "checks_total": len(checks),
        "documented_scope": KNOWN_CLI_STOP_SCOPE if new_only else "NOT_ESTABLISHED",
        "blocking_findings": blockers,
        "hard_cancel_verified": False,
        "tool_dispatch_verified": False,
        "production": "HOLD",
        "G0": "NO-GO", "G_CODE": "NO-GO", "G1": "NO-GO"
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline AST-only ESTOP contract review; never production acceptance")
    parser.add_argument("--estop-source", required=True, type=Path)
    parser.add_argument("--pause-cli", required=True, type=Path)
    parser.add_argument("--estop-git-blob-sha1")
    parser.add_argument("--cli-git-blob-sha1")
    args = parser.parse_args(argv)
    try:
        src, s_receipt = _read_source(args.estop_source, args.estop_git_blob_sha1)
        cli, c_receipt = _read_source(args.pause_cli, args.cli_git_blob_sha1)
        output = inspect_estop_source(src, cli)
        output["inputs"] = {"estop": s_receipt, "pause_cli": c_receipt}
        if not s_receipt["pinned"] or not c_receipt["pinned"]:
            output["blocking_findings"].append("SOURCE_PIN_UNVERIFIED")
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({"status": "SAFE_STOP", "error_type": type(exc).__name__,
                          "error_code": str(exc) if isinstance(exc, ValueError) else "IO_OR_ENCODING_ERROR",
                          "production": "HOLD", "G0": "NO-GO"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
