"""Read-only, fail-closed OFFLINE source-contract inspection for Hermes P0/P1.

This examines Python source files, NEVER imports or runs Hermes. It only identifies
review signals and cannot prove host/runtime enforcement, cancellation, or sandboxing.
No secrets or file contents are included in the report.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path

MAX_SOURCE_BYTES = 2 * 1024 * 1024
FILES = {
    "estop": Path("agent/estop.py"),
    "docker": Path("tools/environments/docker.py"),
    "terminal_backends": Path("tools/terminal_tool_backends.py"),
}


def _is_link(p: Path) -> bool:
    return p.is_symlink() or bool(getattr(p, "is_junction", lambda: False)())


def _read_module(root: Path, relative: Path) -> dict:
    """Return bounded parsed AST or unavailable status. Don't follow links inside root."""
    p = root
    for part in relative.parts:
        if _is_link(p):
            return {"status": "LINK_REFUSED"}
        p = p / part
    if _is_link(p):
        return {"status": "LINK_REFUSED"}
    try:
        with p.open("rb") as stream:
            content = stream.read(MAX_SOURCE_BYTES + 1)
        if len(content) > MAX_SOURCE_BYTES:
            return {"status": "OVERSIZE_REFUSED"}
        text = content.decode("utf-8-sig", errors="strict")
        tree = ast.parse(text, filename=relative.as_posix())
    except FileNotFoundError:
        return {"status": "MISSING"}
    except (PermissionError, IsADirectoryError, OSError):
        return {"status": "INACCESSIBLE"}
    except (UnicodeError, SyntaxError, ValueError):
        return {"status": "UNPARSEABLE"}
    return {"status": "PARSED", "sha256": hashlib.sha256(content).hexdigest(), "tree": tree}


def _names(tree: ast.Module) -> set[str]:
    return {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _literal_global(tree: ast.Module, name: str):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            try:
                return ast.literal_eval(node.value)
            except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
                return None
    return None


def _container_defaults(tree: ast.Module) -> dict:
    entries = _literal_global(tree, "_CONTAINER_KEYS")
    if not isinstance(entries, (list, tuple)):
        return {}
    if any(not isinstance(x, tuple) or len(x) != 2 or not isinstance(x[0], str) for x in entries):
        return {}
    if len({x[0] for x in entries}) != len(entries):
        return {}
    result = {}
    for k, v in entries:
        if k in {"docker_network", "container_persistent", "docker_persist_across_processes",
                 "docker_mount_cwd_to_workspace", "docker_run_as_host_user", "docker_snap_compat"}:
            result[k] = v if isinstance(v, bool) else "UNRESOLVED"
    return result


def audit_source_tree(root: Path) -> dict:
    """Static review only. Never approves production or interprets source as proof of behavior."""
    root = Path(root)
    loaded = {name: _read_module(root, path) for name, path in FILES.items()}
    issues = {"DISPATCH_ENFORCEMENT_UNVERIFIED", "ACTIVE_WORK_TERMINATION_UNVERIFIED",
              "WINDOWS_RUNTIME_UNVERIFIED", "INDEPENDENT_REVIEW_REQUIRED"}
    sources = {name: {k: v for k, v in record.items() if k != "tree"} for name, record in loaded.items()}
    semantic_signals = {
        "estop_entrypoints_declared": False,
        "estop_new_work_only_documented": False,
        "docker_capabilities_added_by_base_policy": "UNKNOWN",
        "docker_no_new_privileges_flag_declared": "UNKNOWN",
        "docker_default_network": "UNKNOWN",
        "docker_default_persistence": "UNKNOWN",
        "docker_default_cross_process_persistence": "UNKNOWN",
    }
    if loaded["estop"]["status"] != "PARSED":
        issues.add("ESTOP_SOURCE_UNAVAILABLE")
    else:
        t = loaded["estop"]["tree"]
        semantic_signals["estop_entrypoints_declared"] = {"is_engaged", "engage", "disengage", "check_paused"}.issubset(_names(t))
        doc = (ast.get_docstring(t) or "").lower()
        semantic_signals["estop_new_work_only_documented"] = ("new work only" in doc and "in-flight" in doc)
        if semantic_signals["estop_new_work_only_documented"]:
            issues.add("ESTOP_STATED_NEW_WORK_ONLY_NOT_KILL_SWITCH")
        else:
            issues.add("ESTOP_SCOPE_UNRESOLVED")
        if not semantic_signals["estop_entrypoints_declared"]:
            issues.add("ESTOP_ENTRYPOINTS_MISSING")
    if loaded["docker"]["status"] != "PARSED":
        issues.add("DOCKER_SOURCE_UNAVAILABLE")
    else:
        t = loaded["docker"]["tree"]
        caps = _literal_global(t, "_BASE_SECURITY_ARGS")
        if isinstance(caps, (tuple, list)) and all(isinstance(x, str) for x in caps):
            semantic_signals["docker_capabilities_added_by_base_policy"] = "--cap-add" in caps
            if "--cap-add" in caps:
                issues.add("DOCKER_BASE_CAPABILITY_ADDITIONS_REQUIRE_REVIEW")
        no_new_privs = _literal_global(t, "_NO_NEW_PRIVILEGES_ARGS")
        if isinstance(no_new_privs, (tuple, list)) and all(isinstance(x, str) for x in no_new_privs):
            semantic_signals["docker_no_new_privileges_flag_declared"] = "no-new-privileges" in no_new_privs
        if semantic_signals["docker_no_new_privileges_flag_declared"] is not True:
            issues.add("NO_NEW_PRIVILEGES_SOURCE_UNVERIFIED")
    if loaded["terminal_backends"]["status"] != "PARSED":
        issues.add("BACKEND_DEFAULT_SOURCE_UNAVAILABLE")
    else:
        defaults = _container_defaults(loaded["terminal_backends"]["tree"])
        semantic_signals["docker_default_network"] = defaults.get("docker_network", "UNKNOWN")
        semantic_signals["docker_default_persistence"] = defaults.get("container_persistent", "UNKNOWN")
        semantic_signals["docker_default_cross_process_persistence"] = defaults.get("docker_persist_across_processes", "UNKNOWN")
        if semantic_signals["docker_default_network"] is not False:
            issues.add("DOCKER_NETWORK_DEFAULT_NOT_PROVEN_OFF")
        if semantic_signals["docker_default_persistence"] is not False:
            issues.add("DOCKER_PERSISTENCE_DEFAULT_NOT_PROVEN_OFF")
        if semantic_signals["docker_default_cross_process_persistence"] is not False:
            issues.add("CROSS_PROCESS_REUSE_DEFAULT_NOT_PROVEN_OFF")
    return {
        "scope": "OFFLINE_STATIC_SOURCE_REVIEW_NOT_RUNTIME_ACCEPTANCE",
        "sources": sources,
        "review_signals": semantic_signals,
        "risk_flags": sorted(issues),
        "assessment": "HOLD",
        "G0": "NO-GO", "G_CODE": "NO-GO", "G1": "NO-GO", "production": "HOLD",
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Hermes P0/P1 bounded source security review")
    p.add_argument("--source-root", required=True, type=Path)
    args = p.parse_args(argv)
    result = audit_source_tree(args.source_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
