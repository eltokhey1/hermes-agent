"""Strict, offline, opt-in mutation checks for *trusted* Python test trees.

This is not a sandbox. The test code executed here must first be assessed as trusted
and run inside an independently isolated disposable VM/container. Never run on
secrets-bearing Windows Hermes or inside a production repo. Standard library only.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_DISCOVERY = re.compile(r'Ran\s+(\d+)\s+tests?\s+in\s+', re.IGNORECASE)
_ASSERTION = re.compile(r'^(?:AssertionError\b|FAIL:\s+\S+)', re.M)
_NON_ASSERT_FAILURE = re.compile(
    r'(?:ModuleNotFoundError|ImportError|_FailedTest|\bERROR:\s+\S+|'
    r'\bsqlite3\.(?:IntegrityError|OperationalError|DatabaseError)|'
    r'^\s*(?!(?:AssertionError)\b)(?:[\w.]*Error|Exception):\s+)', re.M,
)
MAX_COPY_BYTES = 50 * 1024 * 1024


def classify_test_process(returncode: int, output: str, baseline_count: int | None,
                          timed_out: bool = False) -> dict:
    if timed_out:
        return {"classification": "INVALID_TIMEOUT", "discovered": None}
    matches = list(_DISCOVERY.finditer(output))
    count = int(matches[-1].group(1)) if len(matches) == 1 else None
    if count is None or count == 0 or (baseline_count is not None and count != baseline_count):
        return {"classification": "INVALID_DISCOVERY", "discovered": count}
    if "_FailedTest" in output or "ModuleNotFoundError" in output or "ImportError" in output:
        return {"classification": "INVALID_IMPORT", "discovered": count}
    if _NON_ASSERT_FAILURE.search(output):
        return {"classification": "INVALID_RUNTIME", "discovered": count}
    if returncode == 0 and re.search(r'^OK(?:\s*\(.*\))?$', output, re.M) and 'FAILED (' not in output:
        return {"classification": "SURVIVED", "discovered": count}
    if (returncode != 0 and _ASSERTION.search(output)
        and re.search(r'^FAILED \(failures=\d+(?:,\s*skipped=\d+)?\)', output, re.M)):
        return {"classification": "KILLED_ASSERTION", "discovered": count}
    return {"classification": "INVALID_RUNTIME", "discovered": count}


def _run_tests(root: Path, timeout: int) -> dict:
    # Drop common credentials and endpoints. This is defense-in-depth only;
    # subprocess isolation must be provided externally.
    env = {k: v for k, v in os.environ.items() if not any(
        s in k.upper() for s in ("TOKEN", "SECRET", "PASSWORD", "API_KEY", "CREDENTIAL", "AUTH", "PROXY"))}
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1")
    try:
        p = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
            cwd=root, capture_output=True, text=True, timeout=timeout, env=env,
            stdin=subprocess.DEVNULL,
        )
        return {"returncode": p.returncode, "output": (p.stdout + p.stderr)[-200000:], "timed_out": False}
    except subprocess.TimeoutExpired:
        return {"returncode": 124, "output": "", "timed_out": True}


def _validate_relative(relative: str) -> Path:
    p = Path(relative)
    if not relative or p.is_absolute() or '..' in p.parts or '.' in p.parts or '\\' in relative:
        raise ValueError("unsafe relative dependency/mutation path")
    if any(s in ('.git', '.venv', '__pycache__') for s in p.parts):
        raise ValueError("excluded path")
    return p


def _clone_workspace(source: Path, target: Path, required_paths: list[str]) -> None:
    total = 0
    # Always fail on symlinks, even nested ones (copytree follows them by default).
    for rel in required_paths:
        p = _validate_relative(rel)
        src = source / p
        if not src.exists():
            raise FileNotFoundError("required dependency missing: " + rel)
        if any(parent.is_symlink() for parent in (source / Path(*p.parts[:i]) for i in range(1, len(p.parts)+1))):
            raise ValueError("symlink dependency refused")
        dest = target / p
        files = []
        if src.is_dir():
            for root, dirs, filenames in os.walk(src, followlinks=False):
                for name in dirs + filenames:
                    candidate = Path(root) / name
                    if candidate.is_symlink():
                        raise ValueError("nested symlink refused")
                for name in filenames:
                    candidate = Path(root) / name
                    if '__pycache__' in candidate.parts or candidate.suffix == '.pyc':
                        continue
                    if candidate.name in ('.env',) or '.git' in candidate.parts:
                        continue
                    files.append(candidate)
        elif src.is_file():
            files.append(src)
        else:
            raise ValueError("unsupported dependency type")
        for f in files:
            total += f.stat().st_size
            if total > MAX_COPY_BYTES:
                raise ValueError("bounded dependency copy exceeded")
            output = dest / f.relative_to(src) if src.is_dir() else dest
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, output, follow_symlinks=False)
        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)


def evaluate(source: Path, required_paths: list[str], mutants: list[dict], timeout: int = 15) -> dict:
    """Each mutant is {path, old, new}. Never counts import/discovery/runtime errors as kills."""
    source = Path(source).resolve()
    if not source.is_dir() or "tests" not in required_paths or timeout < 1 or timeout > 120:
        raise ValueError("require trusted source, tests dependency and a bounded timeout")
    if len(set(required_paths)) != len(required_paths):
        raise ValueError("duplicate dependencies")
    with tempfile.TemporaryDirectory(prefix="hermes-gate-baseline-") as td:
        try:
            _clone_workspace(source, Path(td), required_paths)
            baseline = _run_tests(Path(td), timeout)
        except (ValueError, FileNotFoundError, OSError) as exc:
            return {"status": "INVALID_BASELINE", "error_type": type(exc).__name__, "mutations": []}
    b = classify_test_process(baseline["returncode"], baseline["output"], None, baseline["timed_out"])
    if b["classification"] != "SURVIVED":
        return {"status": "INVALID_BASELINE", "baseline": b, "mutations": []}
    count = b["discovered"]
    outcomes = []
    for index, m in enumerate(mutants):
        with tempfile.TemporaryDirectory(prefix="hermes-gate-mutant-") as td:
            root = Path(td)
            try:
                _clone_workspace(source, root, required_paths)
                relative = _validate_relative(m["path"])
                path = root / relative
                if not path.is_file() or path.is_symlink():
                    raise ValueError("mutation target missing or symlink")
                original = path.read_text(encoding="utf-8")
                old, new = m["old"], m["new"]
                if not old or original.count(old) != 1 or old == new:
                    raise ValueError("mutation must change exactly one match")
                path.write_text(original.replace(old, new, 1), encoding="utf-8")
                compile(path.read_text(encoding="utf-8"), str(path), 'exec')
                result = _run_tests(root, timeout)
                c = classify_test_process(result["returncode"], result["output"], count, result["timed_out"])
                outcomes.append({"index": index, **c})
            except (ValueError, KeyError, FileNotFoundError, UnicodeError, SyntaxError, OSError) as exc:
                outcomes.append({"index": index, "classification": "INVALID_SETUP",
                                 "error_type": type(exc).__name__, "discovered": None})
    return {
        "status": "OFFLINE_TESTED_ONLY", "baseline_tests": count, "mutations": outcomes,
        "killed_assertion": sum(x["classification"] == "KILLED_ASSERTION" for x in outcomes),
        "invalid": sum(x["classification"].startswith("INVALID") for x in outcomes),
        "survived": sum(x["classification"] == "SURVIVED" for x in outcomes),
        "production": "HOLD", "gates": {"G0": "NO-GO", "G-CODE": "NO-GO", "G1": "NO-GO"},
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: python mutation_gate.py config.json report.json")
    config = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    report = evaluate(Path(config["source"]), config["required_paths"], config["mutants"],
                      int(config.get("timeout", 15)))
    Path(sys.argv[2]).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if report.get("status") == "INVALID_BASELINE" or report.get("invalid"):
        raise SystemExit(2)