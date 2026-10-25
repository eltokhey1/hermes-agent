"""Single-command, dependency-free TradeDocs pilot verification."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
if __name__ == "__main__":
    tests = sorted(p.name for p in ROOT.glob("test_*.py"))
    if not tests:
        raise SystemExit("No tests found")
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT), "-p", "test_*.py", "-v"], cwd=ROOT, check=False)
    raise SystemExit(result.returncode)
