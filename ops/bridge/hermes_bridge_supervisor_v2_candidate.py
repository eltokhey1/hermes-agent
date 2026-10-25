"""Hermes read-only GitHub inbox supervisor v2 (sandbox candidate; not deployed).

Runs ONLY a local, SHA-256-pinned copy of hermes_bridge_v1.py.
It does not evaluate received Python, mutate Hermes, merge or deploy.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import time

WORKER_SHA256 = "f85bf5021fa2e05fc06abb52502932d09952a19fb0c1fcf6f83106158ac4278f"
DEFAULT_WORKER = Path(tempfile.gettempdir()) / "hermes_bridge_v1_verified.py"
STATE_DIR = Path(os.environ.get("LOCALAPPDATA") or tempfile.gettempdir()) / "HermesBridgePilot"


def iso_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def check_worker(worker):
    candidate = Path(worker).resolve(strict=True)
    if not candidate.is_file() or candidate.stat().st_size > 100_000:
        raise ValueError("WORKER_FILE_INVALID")
    digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if digest != WORKER_SHA256:
        raise ValueError("WORKER_HASH_MISMATCH")
    return candidate


def write_status(path, **fields):
    value = {"schema": "hermes.bridge.supervisor.status.v1",
             "timestamp_utc": iso_now(), "production": "HOLD", **fields}
    target = path / "status.json"
    tmp = path / ("status." + str(os.getpid()) + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, sort_keys=True, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, target)
    print(json.dumps(value, sort_keys=True), flush=True)


def run_once(worker):
    """Run one bounded scan; separate process prevents stale state between scans."""
    cmd = [sys.executable, "-I", "-B", "-S", str(worker)]
    try:
        result = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True,
                                text=True, encoding="utf-8", errors="replace",
                                timeout=120, check=False)
    except subprocess.TimeoutExpired:
        return 124, "WORKER_TIMEOUT"
    except OSError:
        return 125, "WORKER_OS_ERROR"
    # Accept only the worker's exact final success line; never infer success
    # from an arbitrary substring in its output.
    if result.returncode == 0:
        if result.stderr.strip():
            return 126, "SCAN_STDERR_UNEXPECTED"
        lines = result.stdout.rstrip().splitlines()
        last = lines[-1] if lines else ""
        if last == "INBOX_MISSING; no action":
            return 126, "INBOX_MISSING"
        if re.fullmatch(r"SCAN_DONE processed=[0-9]+", last):
            return 0, "SCAN_OK"
        return 126, "SCAN_OUTPUT_UNKNOWN"
    # Local allowlisted diagnostic; no worker stdout/stderr or secrets persisted.
    from runpy import run_path
    classifier = run_path(str(Path(__file__).with_name('worker_exit_diagnostics_v1.py')))['classify_worker_exit']
    return result.returncode, classifier(result.returncode)


def main(argv=None):
    p = argparse.ArgumentParser(description="Read-only Hermes bridge supervisor; no code execution")
    p.add_argument("--worker", default=str(DEFAULT_WORKER))
    p.add_argument("--poll", action="store_true", help="repeat until stopped; opt-in")
    p.add_argument("--interval", type=int, default=30)
    args = p.parse_args(argv)
    if not (20 <= args.interval <= 3600):
        p.error("--interval must be between 20 and 3600 seconds")
    try:
        worker = check_worker(args.worker)
        STATE_DIR.mkdir(parents=True, exist_ok=True)
    except (OSError, ValueError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    # Windows: locking a single byte excludes a second instance of this supervisor.
    lock_file = STATE_DIR / "instance.lock"
    with open(lock_file, "a+b") as lock:
        if lock.seek(0, os.SEEK_END) == 0:
            lock.write(b"\x00")
            lock.flush()
        lock.seek(0)
        if os.name == "nt":
            import msvcrt
            lock.seek(0)
            try:
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                print("REFUSED: ANOTHER_SUPERVISOR_IS_RUNNING", file=sys.stderr)
                return 3
        streak = 0
        count = 0
        try:
            while True:
                if hashlib.sha256(worker.read_bytes()).hexdigest() != WORKER_SHA256:
                    write_status(STATE_DIR, state="REFUSED", error="WORKER_CHANGED", scans=count)
                    return 4
                code, result = run_once(worker)
                count += 1
                streak = streak + 1 if code else 0
                write_status(STATE_DIR, state=("HEALTHY" if code == 0 else "DEGRADED"),
                             worker_sha256=WORKER_SHA256, last_scan=result,
                             last_exit_code=code, scans=count, consecutive_failures=streak,
                             polling=args.poll)
                if not args.poll:
                    return 0 if code == 0 else 1
                if streak >= 5:
                    write_status(STATE_DIR, state="STOPPED", error="REPEATED_FAILURES",
                                 scans=count, consecutive_failures=streak)
                    return 5
                time.sleep(min(args.interval * max(1, streak), 300))
        except KeyboardInterrupt:
            write_status(STATE_DIR, state="STOPPED_BY_USER", scans=count)
            return 0
        except OSError:
            write_status(STATE_DIR, state="STOPPED", error="LOCAL_IO_ERROR", scans=count)
            return 6
        finally:
            if os.name == "nt":
                lock.seek(0)
                try:
                    msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass


if __name__ == "__main__":
    raise SystemExit(main())
