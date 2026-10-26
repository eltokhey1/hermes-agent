"""Fail-closed, opt-in startup check for the pinned Hermes read-only bridge.

This launcher only runs fixed SHA256-pinned local files. It does not execute
code received from GitHub, install a service, or change production state.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

WORKER_SHA256 = "f85bf5021fa2e05fc06abb52502932d09952a19fb0c1fcf6f83106158ac4278f"
SUPERVISOR_SHA256 = "edd4ccb304d18089fc7d8d317bf2f1e44358e8b12e5864cb76b9286e1adc8f61"


def check_pin(path, digest):
    path = Path(path).resolve(strict=True)
    if not path.is_file() or path.stat().st_size > 100_000:
        raise ValueError("PINNED_FILE_INVALID")
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError("PINNED_HASH_MISMATCH")
    return path


def healthy_status(status_path, started_at):
    """Require a fresh, successful first scan; old HEALTHY files never qualify."""
    try:
        if Path(status_path).stat().st_size > 8192:
            return False
        status = json.loads(Path(status_path).read_text(encoding="utf-8"))
        stamp = dt.datetime.fromisoformat(status["timestamp_utc"].replace("Z", "+00:00"))
        now = dt.datetime.now(dt.timezone.utc)
        return (stamp.tzinfo is not None and started_at <= stamp <= now + dt.timedelta(seconds=5)
                and status.get("schema") == "hermes.bridge.supervisor.status.v1"
                and status.get("state") == "HEALTHY"
                and status.get("last_scan") == "SCAN_OK"
                and type(status.get("last_exit_code")) is int
                and status["last_exit_code"] == 0
                and type(status.get("consecutive_failures")) is int
                and status["consecutive_failures"] == 0
                and status.get("polling") is True
                and status.get("production") == "HOLD"
                and status.get("worker_sha256") == WORKER_SHA256)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return False


def wait_ready(process, status_path, started_at, timeout=140, interval=1):
    """Verify actual child liveness *and* a new heartbeat; never trust spawn alone."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return "SUPERVISOR_EXITED_EARLY"
        if healthy_status(status_path, started_at):
            return "READY"
        time.sleep(interval)
    return "STARTUP_TIMEOUT"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Hermes pinned read-only supervisor startup gate")
    parser.add_argument("--folder", required=True, help="Existing HermesBridgePilot directory")
    parser.add_argument("--python", default=sys.executable, help="Trusted local Python interpreter")
    parser.add_argument("--timeout", type=int, default=140)
    args = parser.parse_args(argv)
    if not 5 <= args.timeout <= 180:
        parser.error("timeout must be 5..180 seconds")
    folder = Path(args.folder).resolve()
    try:
        worker = check_pin(folder / "hermes_bridge_v1.py", WORKER_SHA256)
        supervisor = check_pin(folder / "hermes_bridge_supervisor_v1.py", SUPERVISOR_SHA256)
        python = Path(args.python).resolve(strict=True)
        if not python.is_file():
            raise ValueError("PYTHON_INVALID")
    except (OSError, ValueError) as exc:
        print(f"REFUSED: {type(exc).__name__}", file=sys.stderr)
        return 2

    output = folder / "scheduled.stdout.log"
    errors = folder / "scheduled.stderr.log"
    started_at = dt.datetime.now(dt.timezone.utc)
    try:
        with output.open("ab") as stdout, errors.open("ab") as stderr:
            process = subprocess.Popen(
                [str(python), "-I", "-B", "-S", str(supervisor), "--worker",
                 str(worker), "--poll", "--interval", "30"],
                cwd=str(folder), stdin=subprocess.DEVNULL,
                stdout=stdout, stderr=stderr, close_fds=True,
                creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0),
                start_new_session=(os.name != "nt"),
            )
            result = wait_ready(process, folder / "status.json", started_at,
                                timeout=args.timeout)
            if result == "READY":
                print("SUPERVISOR_STARTUP=READY; PRODUCTION=HOLD")
                return 0
            # Only terminate the newly spawned child, never other processes or services.
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
            print(f"SUPERVISOR_STARTUP={result}; PRODUCTION=HOLD", file=sys.stderr)
            return 1
    except OSError as exc:
        print(f"SUPERVISOR_STARTUP=OS_ERROR_{type(exc).__name__}; PRODUCTION=HOLD", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
