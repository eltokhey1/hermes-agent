#!/usr/bin/env python3
"""Hermes P0 metadata-only local inventory. Reads Git metadata, never project file contents.

This intentionally does not run Hermes, import project modules, write reports, copy
secrets, call remote services, access Git remote URLs, or modify the working tree.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

SCHEMA = "hermes-owner-p0-inventory/v1"
GIT_TIMEOUT_SECONDS = 15
# No user-provided command arguments, no shell, and no network commands.
GIT_PREFIX = ("git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-c", "submodule.recurse=false")


class InventoryError(Exception):
    """Generic error; do not attach paths, credentials or stderr."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _git(repo: Path, *arguments: str) -> str:
    command = [*GIT_PREFIX, "-C", str(repo), *arguments]
    # Git-specific inherited environment can redirect repository identity or write trace logs.
    # Preserve normal process variables (PATH/SystemRoot/etc.), but isolate Git overrides.
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    try:
        process = subprocess.run(command, capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", check=False,
                                 timeout=GIT_TIMEOUT_SECONDS, env=env)
    except FileNotFoundError as exc:
        raise InventoryError("GIT_NOT_AVAILABLE") from exc
    except subprocess.TimeoutExpired as exc:
        raise InventoryError("GIT_TIMEOUT") from exc
    except OSError as exc:
        raise InventoryError("GIT_COMMAND_FAILED") from exc
    if process.returncode != 0:
        # In particular, *never* relay Git stderr: it may include paths or URLs.
        raise InventoryError("GIT_COMMAND_FAILED")
    return process.stdout.strip()


def _counts(status_text: str) -> dict[str, int | bool]:
    """Aggregate porcelain v1 statuses without leaking filenames."""
    # Git porcelain v1 uses LF records; splitlines() also splits Unicode U+2028 in paths.
    lines = status_text.split("\n") if status_text else []
    unknown = sum(line.startswith("??") for line in lines)
    tracked = len(lines) - unknown
    return {"tracked_changes": tracked, "untracked_entries": unknown,
            "working_tree_dirty": bool(lines)}


def _is_windows() -> bool:
    """Isolated platform predicate so tests need not monkeypatch global sys.platform."""
    return sys.platform == "win32"


def collect(repo: Path) -> dict:
    if shutil.which("git") is None:
        raise InventoryError("GIT_NOT_AVAILABLE")
    repo = repo.expanduser().resolve()
    if not repo.is_dir():
        raise InventoryError("NOT_A_DIRECTORY")
    try:
        inside = _git(repo, "rev-parse", "--is-inside-work-tree")
    except InventoryError as exc:
        if exc.code == "GIT_COMMAND_FAILED":
            raise InventoryError("NOT_A_GIT_REPOSITORY") from exc
        raise
    if inside != "true":
        raise InventoryError("NOT_A_GIT_REPOSITORY")
    root = Path(_git(repo, "rev-parse", "--show-toplevel"))
    # Prevent a requested child directory from silently inheriting an unrelated parent Git repo.
    # Normalize Windows case and resolve symlinks/reparse points before comparison.
    if os.path.normcase(str(root.resolve())) != os.path.normcase(str(repo)):
        raise InventoryError("REPOSITORY_ROOT_MISMATCH")
    sha = _git(root, "rev-parse", "--verify", "HEAD")
    if len(sha) != 40 or any(c not in "0123456789abcdefABCDEF" for c in sha):
        raise InventoryError("INVALID_HEAD")
    # No branch names, filenames, paths, remote URLs, or environment variables
    # appear in the JSON; these could encode personal data / secrets.
    branch = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    # A dirty submodule must not make the checkout appear clean.
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=normal",
                  "--ignore-submodules=none")
    remote_names = _git(root, "remote")
    markers = ("AGENTS.md", "README.md", "scripts/run_tests.sh", "pyproject.toml")
    marker_presence = {name: (root / name).is_file() for name in markers}
    local_app_data = os.environ.get("LOCALAPPDATA")
    # Missing or relative LOCALAPPDATA must not prove an installed runtime.
    install_dir = (
        Path(local_app_data) / "hermes"
        if _is_windows() and local_app_data and Path(local_app_data).is_absolute()
        else None
    )
    result = {
        "schema": SCHEMA,
        "checked_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "platform": sys.platform,
        "repository_detected": True,
        "head_sha": sha.lower(),
        "branch_is_main": branch == "main",
        "detached_head": branch == "HEAD",
        "configured_remote_present": bool(remote_names),
        "project_markers": marker_presence,
        "docker_cli_on_path": shutil.which("docker") is not None,
        "hermes_windows_install_directory_present": (install_dir.is_dir() if install_dir is not None else None),
        **_counts(status),
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only Hermes P0 metadata inventory. Outputs sanitized JSON to stdout.")
    parser.add_argument("--repo", default=".", help="Repository directory; not included in output")
    args = parser.parse_args(argv)
    try:
        report = collect(Path(args.repo))
        exit_code = 0
    except InventoryError as exc:
        report = {"schema": SCHEMA, "repository_detected": False, "error_code": exc.code}
        exit_code = 2
    except Exception:
        # No leaking unexpected exception text, environment or stack traces.
        report = {"schema": SCHEMA, "repository_detected": False, "error_code": "UNEXPECTED_ERROR"}
        exit_code = 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
