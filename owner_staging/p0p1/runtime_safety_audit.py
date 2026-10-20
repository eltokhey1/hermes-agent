"""Hermes P0 offline, READ-ONLY, fail-closed risk audit (stdlib only).

Not an effective configuration parser, security sandbox, ESTOP test, or production
acceptance. Does not import Hermes, launch Docker, execute a model, write files,
read secret values in output, or call remote services.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path

_BACKENDS = {"local", "docker", "ssh", "modal", "daytona", "singularity", "vercel_sandbox", "managed_modal"}
_BOOLEAN_KEYS = {
    "docker_network", "docker_mount_cwd_to_workspace", "docker_run_as_host_user",
    "container_persistent", "docker_persist_across_processes", "docker_snap_compat",
}
_SENSITIVE_KEYS = {
    "docker_volumes", "docker_extra_args", "docker_forward_env", "docker_env",
    "docker_shared_container_key", "docker_ecr_credentials", "docker_registry_auth",
}
_OVERRIDE_KEYS = (
    "HERMES_HOME", "TERMINAL_ENV", "TERMINAL_BACKEND", "TERMINAL_DOCKER_NETWORK",
    "TERMINAL_DOCKER_VOLUMES", "TERMINAL_DOCKER_EXTRA_ARGS", "TERMINAL_DOCKER_FORWARD_ENV",
    "TERMINAL_DOCKER_ENV", "TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE",
    "TERMINAL_CONTAINER_PERSISTENT", "TERMINAL_DOCKER_PERSIST_ACROSS_PROCESSES",
)
_SIMPLE_KEY = re.compile(r"^([ \t]*)([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")
_HEADER = re.compile(r"^terminal\s*:\s*(?:#.*)?$")
_SHA256 = re.compile(r"[0-9a-fA-F]{64}\Z")


def _simple_scalar(value: str) -> str | None:
    """Only literal scalars, NOT full YAML; reject aliases/tags/complex content."""
    value = value.strip()
    if value.startswith(('"', "'")):
        quote = value[0]
        if len(value) < 2 or value[-1] != quote or value.count(quote) != 2:
            return None
        return value[1:-1]
    value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        return None
    return value


def assess_config(text: str) -> dict:
    """Conservative static inspection. Never include config values other than allowlisted booleans/backend."""
    if len(text.encode("utf-8")) > 1024 * 1024:
        return {"backend": "UNKNOWN", "docker_network": "UNKNOWN", "terminal_section": "TOO_LARGE",
                "sensitive_keys_present": [], "risk_flags": ["CONFIG_TOO_LARGE"], "assessment": "HOLD"}
    terminal_count = 0
    in_terminal = False
    entries: dict[str, str] = {}
    duplicate_keys: set[str] = set()
    indent = None
    complex_config = False
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) is False:
            in_terminal = bool(_HEADER.fullmatch(line))
            if in_terminal:
                terminal_count += 1
                indent = None
            continue
        if not in_terminal:
            continue
        match = _SIMPLE_KEY.match(line)
        if match is None:
            # A nested array or multiline YAML value; do not guess its semantics.
            complex_config = True
            continue
        whitespace, key, val = match.groups()
        if "\t" in whitespace:
            complex_config = True
            continue
        depth = len(whitespace)
        if indent is None:
            indent = depth
        if depth != indent:
            continue
        if key in entries:
            duplicate_keys.add(key)
        entries[key] = val

    issues = []
    if terminal_count == 0:
        issues.append("TERMINAL_SECTION_MISSING")
    if terminal_count > 1:
        issues.append("MULTIPLE_TERMINAL_SECTIONS")
    if duplicate_keys:
        issues.append("DUPLICATE_TERMINAL_KEYS")
    if complex_config:
        issues.append("COMPLEX_YAML_UNRESOLVED")

    backend = _simple_scalar(entries.get("backend", ""))
    if backend not in _BACKENDS:
        backend = "UNKNOWN"
        issues.append("BACKEND_UNKNOWN_OR_ABSENT")
    elif backend != "docker":
        issues.append("BACKEND_NOT_DOCKER")

    net_raw = _simple_scalar(entries.get("docker_network", "")) if "docker_network" in entries else None
    if net_raw is None and "docker_network" not in entries and backend == "docker":
        network = "DEFAULT_TRUE_PER_REVIEWED_SOURCE"
    elif net_raw in {"true", "false"}:
        network = net_raw.upper()
    else:
        network = "UNKNOWN"
    if backend == "docker" and network != "FALSE":
        issues.append("NETWORK_NOT_PROVEN_DISABLED")

    mount_raw = _simple_scalar(entries.get("docker_mount_cwd_to_workspace", "")) if "docker_mount_cwd_to_workspace" in entries else None
    if backend == "docker" and mount_raw not in {None, "false"}:
        issues.append("HOST_CWD_MOUNT_POSSIBLE")
    if backend == "docker" and any(k in entries and entries[k].strip() != "[]" for k in ("docker_volumes", "docker_extra_args", "docker_forward_env", "docker_env")):
        issues.append("DOCKER_MOUNT_ENV_OR_EXTRA_ARGS_NEED_REVIEW")
    if backend == "docker":
        for key in ("container_persistent", "docker_persist_across_processes"):
            value = _simple_scalar(entries.get(key, "")) if key in entries else None
            if value != "false":
                issues.append("CONTAINER_OR_SESSION_PERSISTENCE_NOT_DISABLED")
                break
        if _simple_scalar(entries.get("docker_snap_compat", "")) == "true":
            issues.append("DOCKER_SNAP_COMPAT_WEAKENS_NNP")

    # Even a seemingly safe config never constitutes effective runtime evidence.
    issues.append("LIVE_RUNTIME_AND_TOOL_DISPATCH_UNVERIFIED")
    issues.append("ESTOP_ACTIVE_WORK_CANCELLATION_UNVERIFIED")
    issues.append("FUNCTIONAL_RESTORE_UNVERIFIED")
    return {
        "terminal_section": "SINGLE" if terminal_count == 1 else ("MISSING" if not terminal_count else "AMBIGUOUS"),
        "backend": backend,
        "docker_network": network,
        "sensitive_keys_present": sorted(k for k in entries if k in _SENSITIVE_KEYS),
        "risk_flags": sorted(set(issues)),
        "assessment": "HOLD",
    }


def _check_no_link(path: Path) -> bool:
    # Check the file itself. Not a recursive symlink traversal or a replacement for ACL checks.
    try:
        return not path.is_symlink() and not (hasattr(path, "is_junction") and path.is_junction())
    except OSError:
        return False


def _marker_exists(path: Path) -> str:
    try:
        if not _check_no_link(path):
            return "LINK_OR_UNVERIFIED"
        return "PRESENT" if path.exists() else "ABSENT"
    except OSError:
        return "UNREADABLE"


def audit_hermes_home(home: Path, env: dict[str, str] | None = None) -> dict:
    env = os.environ if env is None else env
    home = Path(home)
    cfg = home / "config.yaml"
    result = {
        "config": "MISSING_OR_INACCESSIBLE",
        "terminal": assess_config(""),
        "estop_marker_in_active_home": _marker_exists(home / "ESTOP"),
        "estop_marker_in_legacy_home": _marker_exists(Path.home() / ".hermes" / "ESTOP"),
        "environment_override_names": sorted(k for k in _OVERRIDE_KEYS if k in env),
        "effective_backend_verified": False,
        "estop_dispatch_verified": False,
        "estop_cancels_in_flight_verified": False,
        "backup_complete_verified": False,
        "production": "HOLD",
        "G0": "NO-GO", "G_CODE": "NO-GO", "G1": "NO-GO",
    }
    try:
        if not _check_no_link(cfg):
            result["config"] = "LINK_OR_UNVERIFIED"
        elif cfg.is_file():
            # Limit amount read. A too-large file remains unresolved.
            with cfg.open("rb") as stream:
                contents = stream.read(1024 * 1024 + 1)
            result["config"] = "READABLE_STATIC_ONLY"
            try:
                result["terminal"] = assess_config(contents.decode("utf-8-sig", errors="strict"))
            except UnicodeError:
                result["config"] = "ENCODING_UNVERIFIED"
    except OSError:
        result["config"] = "UNREADABLE"
    if result["environment_override_names"]:
        result["terminal"]["risk_flags"] = sorted(set(result["terminal"]["risk_flags"] + ["PROCESS_OVERRIDE_PRESENT_NOT_RESOLVED"]))
    return result


def verify_backup(path: Path, expected: str) -> dict:
    """Hash only; no decryption and no filename/secret disclosure."""
    if not _SHA256.fullmatch(expected):
        return {"result": "INVALID_EXPECTED_HASH"}
    path = Path(path)
    if not _check_no_link(path):
        return {"result": "LINK_OR_UNVERIFIED"}
    try:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return {"result": "SHA256_MATCH" if digest.hexdigest() == expected.lower() else "SHA256_MISMATCH"}
    except OSError:
        return {"result": "READ_ERROR_OR_MISSING"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Hermes conservative P0 read-only risk assessment")
    ap.add_argument("--hermes-home", type=Path, required=True)
    ap.add_argument("--verify-backup", nargs=2, action="append", metavar=("ARCHIVE", "SHA256"), default=[])
    args = ap.parse_args(argv)
    result = audit_hermes_home(args.hermes_home)
    result["backup_checks"] = [verify_backup(Path(path), sha) for path, sha in args.verify_backup]
    result["assessment_scope"] = "OFFLINE_READ_ONLY_STATIC_NON_ACCEPTANCE"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
