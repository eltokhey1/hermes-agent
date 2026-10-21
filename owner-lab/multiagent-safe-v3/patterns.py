"""Deterministic, zero-provider examples of multi-agent *patterns*.

This module does not run LLMs, tools, plugins or subprocesses. Every output is
an inert proposal; callers MUST apply an independent policy and evidence gate.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping


class WorkflowDenied(ValueError):
    pass


@dataclass(frozen=True)
class Proposal:
    specialist: str
    summary: str
    confidence: float
    evidence_ids: tuple[str, ...]

    def __post_init__(self):
        if self.specialist not in {'research', 'code', 'data', 'qa'}:
            raise WorkflowDenied('Unknown specialist')
        if not isinstance(self.summary, str) or not 1 <= len(self.summary) <= 2000:
            raise WorkflowDenied('Invalid summary')
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool) or not 0 <= self.confidence <= 1:
            raise WorkflowDenied('Invalid confidence')
        if not isinstance(self.evidence_ids, tuple) or not self.evidence_ids or not all(
            isinstance(i, str) and 1 <= len(i) <= 100 for i in self.evidence_ids
        ):
            raise WorkflowDenied('Missing evidence')


def route(task_type: str) -> str:
    """Allowlisted routing; unsupported work is denied rather than delegated."""
    mapping = {'investigate': 'research', 'modify_code': 'code', 'analyze': 'data', 'verify': 'qa'}
    if task_type not in mapping:
        raise WorkflowDenied('Unknown task route')
    return mapping[task_type]


def fanout_synthesize(proposals: Mapping[str, Proposal]) -> dict:
    """Validate complete evidence-backed proposals; synthesis makes no tool calls."""
    if not proposals or len(proposals) > 4:
        raise WorkflowDenied('Invalid fanout width')
    for specialist, proposal in proposals.items():
        if not isinstance(proposal, Proposal) or specialist != proposal.specialist:
            raise WorkflowDenied('Untrusted specialist output')
        if proposal.confidence < .7:
            raise WorkflowDenied('Insufficient confidence; human review required')
    return {
        'status': 'PROPOSED_ONLY',
        'contributions': {key: value.summary for key, value in sorted(proposals.items())},
        'evidence_ids': sorted({item for p in proposals.values() for item in p.evidence_ids}),
        'external_effects': False,
    }


def evaluator_optimizer(candidate: Proposal, evaluator: Callable[[Proposal], bool],
                        improve: Callable[[Proposal], Proposal], *, max_iterations: int = 2) -> Proposal:
    """Bounded feedback loop; no infinite retries or implicit approval."""
    if not isinstance(candidate, Proposal) or type(max_iterations) is not int or not 0 <= max_iterations <= 3:
        raise WorkflowDenied('Invalid evaluation contract')
    for attempt in range(max_iterations + 1):
        if evaluator(candidate) is True:
            return candidate
        if attempt == max_iterations:
            break
        candidate = improve(candidate)
        if not isinstance(candidate, Proposal):
            raise WorkflowDenied('Malformed improvement')
    raise WorkflowDenied('Independent verification did not pass')


def bounded_handoff(start: str, graph: Mapping[str, str], *, max_handoffs: int = 3) -> tuple[str, ...]:
    """Illustrate peer handoff with strict bounds and no arbitrary agent names."""
    allowed = {'research', 'code', 'data', 'qa'}
    if start not in allowed or type(max_handoffs) is not int or not 0 <= max_handoffs <= 3:
        raise WorkflowDenied('Invalid handoff contract')
    path = [start]
    while path[-1] in graph:
        dest = graph[path[-1]]
        if dest not in allowed or dest in path or len(path) > max_handoffs:
            raise WorkflowDenied('Handoff loop or policy violation')
        path.append(dest)
    return tuple(path)
