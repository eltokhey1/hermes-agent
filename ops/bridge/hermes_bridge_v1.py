"""Hermes GitHub transport v1: receive public Python code as DATA; reply with AST review.

Safety: no execution of submitted code; no local Hermes mutation, secrets, deploy,
merge, subprocess shell, or automatic Aider invocation. Manual start only.
"""
import argparse
import ast
import base64
import datetime as dt
import hashlib
import json
import re
import subprocess
import time
from urllib.parse import quote

REPO = "eltokhey1/hermes-agent"
BRANCH = "sandbox/hermes-transport-smoke-20261025"
INBOX = "ops/bridge/inbox"
OUTBOX = "ops/bridge/outbox"
JOB_RE = re.compile(r"job-[0-9]{8}-[0-9]{2}\.json\Z")
MAX_JOBS = 50
MAX_FILE = 32_768
MAX_SOURCE = 8_192


def github(path, *, method="GET", fields=None):
    """Call GitHub with authenticated local gh CLI; never interpolate a shell command."""
    endpoint = f"repos/{REPO}/contents/{path}"
    if method == "GET":
        endpoint += "?ref=" + quote(BRANCH, safe="")
    argv = ["gh", "api", endpoint]
    if method != "GET":
        argv += ["--method", method]
        for key, value in fields.items():
            argv += ["--raw-field", f"{key}={value}"]
    result = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=35)
    if result.returncode:
        if method == "GET" and "404" in result.stderr:
            return None
        raise RuntimeError("GitHub API error; check 'gh auth status', repository access and branch")
    return json.loads(result.stdout)


def decode_content(data):
    if data is None:
        return None
    if data.get("type") != "file" or data.get("encoding") != "base64":
        raise ValueError("Expected a base64-encoded GitHub file")
    size = int(data.get("size", MAX_FILE + 1))
    if not 0 <= size <= MAX_FILE:
        raise ValueError("Job file exceeds maximum size")
    try:
        raw = base64.b64decode("".join(data["content"].split()), validate=True)
    except (KeyError, AttributeError, ValueError, base64.binascii.Error) as exc:
        raise ValueError("Invalid GitHub base64 content") from exc
    if len(raw) != size:
        raise ValueError("GitHub file size mismatch")
    return raw


def review_task(filename, raw):
    """Untrusted source is *parsed only*, never imported, compiled or executed."""
    job_id = filename[:-5]
    result = {"schema": "hermes.bridge.receipt.v1", "job_id": job_id,
              "status": "REJECTED", "operation": "python_ast_check",
              "executed": False, "production": "HOLD", "isolation": "NOT_PROVEN",
              "completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
    try:
        if len(raw) > MAX_FILE:
            raise ValueError("JOB_TOO_LARGE")
        task = json.loads(raw.decode("utf-8", errors="strict"))
        if not isinstance(task, dict) or task.get("schema") != "hermes.bridge.job.v1":
            raise ValueError("SCHEMA_INVALID")
        if task.get("job_id") != job_id or task.get("operation") != "python_ast_check":
            raise ValueError("JOB_ID_OR_OPERATION_INVALID")
        if task.get("approval") != "read_only":
            raise ValueError("APPROVAL_INVALID")
        source = task.get("source")
        if not isinstance(source, str) or len(source.encode("utf-8")) > MAX_SOURCE or "\x00" in source:
            raise ValueError("SOURCE_INVALID")
        digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
        if task.get("source_sha256") != digest:
            raise ValueError("SOURCE_HASH_MISMATCH")
        result["source_sha256"] = digest
        result["line_count"] = len(source.splitlines())
        try:
            tree = ast.parse(source, filename="<received-code>")
        except SyntaxError as exc:
            result.update(status="SYNTAX_ERROR", error_code="SYNTAX_ERROR", line=exc.lineno)
        else:
            result.update(status="PASS", function_names=[node.name for node in tree.body
                                                         if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))][:25],
                          class_names=[node.name for node in tree.body if isinstance(node, ast.ClassDef)][:25])
    except (ValueError, UnicodeError, KeyError, TypeError, json.JSONDecodeError) as exc:
        result["error_code"] = str(exc) if isinstance(exc, ValueError) and str(exc) in {
            "JOB_TOO_LARGE", "SCHEMA_INVALID", "JOB_ID_OR_OPERATION_INVALID",
            "APPROVAL_INVALID", "SOURCE_INVALID", "SOURCE_HASH_MISMATCH"} else "MALFORMED_JOB"
    return result


def scan_once(api=github):
    listings = api(INBOX)
    if listings is None:
        print("INBOX_MISSING; no action", flush=True)
        return 0
    if not isinstance(listings, list) or len(listings) > MAX_JOBS:
        raise RuntimeError("Inbox not a directory or contains too many files")
    processed = 0
    for entry in sorted(listings, key=lambda x: x.get("name", "")):
        filename = entry.get("name", "")
        if not JOB_RE.fullmatch(filename) or entry.get("type") != "file":
            continue
        receipt_path = OUTBOX + "/" + filename
        if api(receipt_path) is not None:
            continue  # Idempotent: never overwrite an existing response
        item = api(INBOX + "/" + filename)
        raw = decode_content(item)
        receipt = review_task(filename, raw)
        payload = base64.b64encode((json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode()).decode("ascii")
        api(receipt_path, method="PUT", fields={
            "message": f"test: bridge response {filename} [skip ci]", "branch": BRANCH, "content": payload})
        processed += 1
        print(f"REPLIED {filename} STATUS={receipt['status']} EXECUTED=False", flush=True)
    print(f"SCAN_DONE processed={processed}", flush=True)
    return processed


def main():
    parser = argparse.ArgumentParser(description="One-way code-data review with GitHub reply; NO code execution")
    parser.add_argument("--poll", action="store_true", help="poll inbox until interrupted; explicit opt-in")
    parser.add_argument("--interval", type=int, default=30)
    args = parser.parse_args()
    if not 20 <= args.interval <= 3600:
        parser.error("interval must be between 20 and 3600 seconds")
    try:
        while True:
            scan_once()
            if not args.poll:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("BRIDGE_STOPPED", flush=True)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"BRIDGE_ERROR {type(exc).__name__}: {exc}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
