"""Read-only, stdlib-only inventory of nonstandard GitHub Actions runner labels.

This is static source scanning, NOT a claim about runner registration, billing,
availability, job completion, or production acceptance. It never calls GitHub.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

RUNNER_LABEL = re.compile(
    r"\b(?:blacksmith-[A-Za-z0-9_-]+|windows-latest-[0-9]+-arm-core)\b"
)


def audit(root: Path) -> dict:
    folder = root / ".github" / "workflows"
    paths = sorted((*folder.glob("*.yml"), *folder.glob("*.yaml")))
    if not paths:
        raise ValueError("No workflow files; cannot attest runner inventory")
    counts: Counter[str] = Counter()
    used_by: dict[str, list[str]] = {}
    for path in paths:
        relative = path.relative_to(root).as_posix()
        for label in sorted(set(RUNNER_LABEL.findall(path.read_text(encoding="utf-8-sig")))):
            counts[label] += 1
            used_by.setdefault(label, []).append(relative)
    return {
        "schema": "hermes.owner.fork.runner_static.v1",
        "read_only": True,
        "workflow_files_scanned": len(paths),
        "runner_pool_available": "NOT_ATTESTED",
        "strict_ci_passed": "NOT_ATTESTED",
        "special_runner_references": {k: {"file_count": counts[k], "files": used_by[k]} for k in sorted(counts)},
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = p.parse_args()
    report = audit(args.repo_root.resolve())
    print(json.dumps(report, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
