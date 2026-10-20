"""Hermes P0/P1 offline-only deterministic planning gate (no imports from live Hermes).

Turns a validated, bounded multi-agent task graph into an advisory dispatch plan.
Never calls tools, writes state, grants approvals, contacts the network or executes agents.
No plan here is permission to run actions. Production gates remain NO-GO/HOLD.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import defaultdict
from typing import Any

MAX_TASKS = 45  # One work item per canonical work package (not a new registry)
MAX_DEPENDENCIES = 15
MAX_STRING = 128
MAX_STEPS = 45
ALLOWED_ROLES = frozenset({
    "Observer", "Verifier", "Predictor", "Economist", "Risk", "Planner",
    "Executor", "Auditor",
})
# Candidate means scheduling proposal ONLY. This module has no dispatch capability.
ALLOWED_ACTIONS = frozenset({"READ_ONLY", "CODE_WRITE", "NETWORK", "DELETE", "FINANCIAL", "PRODUCTION"})
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_HASH = re.compile(r"^[a-f0-9]{64}$")
EXPECTED_GATES = {"G0": "NO-GO", "G_CODE": "NO-GO", "G1": "NO-GO", "production": "HOLD"}


class InvalidPlan(ValueError):
    """Structural failure: do not schedule or silently omit any task."""


def _number(value: Any, label: str, low: float, high: float, *, strict_min: bool = False) -> float:
    if type(value) not in (int, float):
        raise InvalidPlan("INVALID_NUMBER:" + label)
    number = float(value)
    if not math.isfinite(number) or (number <= low if strict_min else number < low) or number > high:
        raise InvalidPlan("OUT_OF_RANGE:" + label)
    return number


def _validate_task(task: Any) -> dict:
    if not isinstance(task, dict):
        raise InvalidPlan("INVALID_TASK")
    required = {"id", "role", "action", "dependencies", "impact", "confidence", "urgency", "effort", "estimated_cost_usd"}
    if set(task) != required:
        raise InvalidPlan("UNKNOWN_OR_MISSING_TASK_FIELDS")
    ident = task["id"]
    if not isinstance(ident, str) or not _ID.fullmatch(ident):
        raise InvalidPlan("INVALID_TASK_ID")
    if (not isinstance(task["role"], str) or not isinstance(task["action"], str)
            or task["role"] not in ALLOWED_ROLES or task["action"] not in ALLOWED_ACTIONS):
        raise InvalidPlan("UNKNOWN_ROLE_OR_ACTION")
    deps = task["dependencies"]
    if not isinstance(deps, list) or len(deps) > MAX_DEPENDENCIES or any(not isinstance(d, str) or not _ID.fullmatch(d) for d in deps):
        raise InvalidPlan("INVALID_DEPENDENCIES")
    if len(set(deps)) != len(deps) or ident in deps:
        raise InvalidPlan("DUPLICATE_OR_SELF_DEPENDENCY")
    impact = _number(task["impact"], "impact", 0, 10)
    confidence = _number(task["confidence"], "confidence", 0, 1)
    urgency = _number(task["urgency"], "urgency", 0, 10)
    effort = _number(task["effort"], "effort", 0, 100, strict_min=True)
    cost = _number(task["estimated_cost_usd"], "estimated_cost_usd", 0, 1_000_000)
    result = {"id": ident, "role": task["role"], "action": task["action"], "dependencies": list(deps),
              "impact": impact, "confidence": confidence, "urgency": urgency, "effort": effort,
              "estimated_cost_usd": cost}
    result["priority_score"] = round(impact * confidence * urgency / effort, 6)
    return result


def _topological_check(tasks: dict[str, dict]) -> None:
    states: dict[str, int] = {}
    def visit(key: str) -> None:
        if states.get(key) == 1:
            raise InvalidPlan("DEPENDENCY_CYCLE")
        if states.get(key) == 2:
            return
        states[key] = 1
        for parent in tasks[key]["dependencies"]:
            if parent not in tasks:
                raise InvalidPlan("UNKNOWN_DEPENDENCY")
            visit(parent)
        states[key] = 2
    for ident in sorted(tasks):
        visit(ident)


def _canonical_digest(task: dict) -> str:
    safe = {key: value for key, value in task.items() if key != "priority_score"}
    return hashlib.sha256(json.dumps(safe, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def plan_tasks(request: dict) -> dict:
    """Compute advisory proposals only. All risks must fail closed, no execution under any gate."""
    if not isinstance(request, dict) or set(request) != {"tasks", "completed", "limits", "estop_engaged", "gates"}:
        raise InvalidPlan("INVALID_REQUEST_SCHEMA")
    raw = request["tasks"]
    if not isinstance(raw, list) or not 1 <= len(raw) <= MAX_TASKS:
        raise InvalidPlan("INVALID_TASK_COUNT")
    tasks: dict[str, dict] = {}
    for item in raw:
        task = _validate_task(item)
        if task["id"] in tasks:
            raise InvalidPlan("DUPLICATE_TASK_ID")
        tasks[task["id"]] = task
    _topological_check(tasks)
    completed = request["completed"]
    if not isinstance(completed, dict) or not set(completed) <= set(tasks):
        raise InvalidPlan("INVALID_COMPLETED_SET")
    if any(not isinstance(x, str) or not _HASH.fullmatch(x) for x in completed.values()):
        raise InvalidPlan("MISSING_COMPLETION_EVIDENCE")
    limits = request["limits"]
    if not isinstance(limits, dict) or set(limits) != {"max_usd", "max_steps", "max_tool_calls"}:
        raise InvalidPlan("INVALID_LIMITS_SCHEMA")
    budget = _number(limits["max_usd"], "max_usd", 0, 1_000_000)
    steps = limits["max_steps"]
    tool_calls = limits["max_tool_calls"]
    if type(steps) is not int or not 0 <= steps <= MAX_STEPS or type(tool_calls) is not int or not 0 <= tool_calls <= MAX_STEPS:
        raise InvalidPlan("INVALID_STEP_OR_TOOL_CAP")
    if type(request["estop_engaged"]) is not bool:
        raise InvalidPlan("ESTOP_UNKNOWN")
    if request["gates"] != EXPECTED_GATES:
        raise InvalidPlan("UNVERIFIED_GATE_STATUS")
    ordered = sorted(tasks.values(), key=lambda t: (-t["priority_score"], t["id"]))
    proposed = []
    projected_cost = 0.0
    selected = 0
    for t in ordered:
        if t["id"] in completed:
            decision = "COMPLETED_EVIDENCE_ONLY"
        elif request["estop_engaged"]:
            decision = "ESTOP_HOLD"
        elif t["action"] != "READ_ONLY":
            decision = "HUMAN_APPROVAL_AND_GATE_REQUIRED"
        elif any(dep not in completed for dep in t["dependencies"]):
            decision = "DEPENDENCY_PENDING"
        elif tool_calls == 0 or selected >= steps or selected >= tool_calls:
            decision = "STEP_OR_TOOL_LIMIT"
        elif projected_cost + t["estimated_cost_usd"] > budget + 1e-9:
            decision = "BUDGET_LIMIT"
        else:
            # A proposal, NOT executable authorization; no tool invocation in this module.
            decision = "CANDIDATE_READ_ONLY_NOT_AUTHORIZED"
            projected_cost += t["estimated_cost_usd"]
            selected += 1
        proposed.append({"id": t["id"], "role": t["role"], "action": t["action"],
                         "priority_score": t["priority_score"], "decision": decision,
                         "dependencies": t["dependencies"], "task_digest": _canonical_digest(t)})
    return {"scope": "OFFLINE_ADVISORY_ONLY", "decisions": proposed,
            "count": len(proposed), "proposed_steps": selected,
            "projected_cost_usd": round(projected_cost, 6),
            "execution_performed": False, "sandbox_verified": False, "completion_evidence_verified_externally": False,
            "G0": "NO-GO", "G_CODE": "NO-GO", "G1": "NO-GO", "production": "HOLD"}


def main(argv: list[str] | None = None) -> int:
    """CLI reads a JSON file; prints only decisions/digests, not task content or secrets."""
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description="Hermes offline advisory planner (never execution)")
    parser.add_argument("--request", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.request.is_symlink() or args.request.stat().st_size > 256 * 1024:
            raise InvalidPlan("INVALID_INPUT_FILE")
        with args.request.open("r", encoding="utf-8") as stream:
            request = json.load(stream)
        output = plan_tasks(request)
    except (InvalidPlan, OSError, UnicodeError, ValueError, RecursionError):
        print(json.dumps({"status": "SAFE_STOP", "execution_performed": False,
                          "G0": "NO-GO", "G_CODE": "NO-GO", "G1": "NO-GO", "production": "HOLD"}))
        return 2
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
