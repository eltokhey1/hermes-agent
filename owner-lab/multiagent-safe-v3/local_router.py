"""Fail-closed *planning only* for no-cloud Hermes/Kilo/Aider/OpenCode model routing.

Does not probe PATH, invoke subprocesses, use network or mutate config.
Availability MUST be supplied by a trusted local read-only preflight.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import FrozenSet


class RoutingDenied(ValueError):
    pass


@dataclass(frozen=True)
class LocalInventory:
    installed_tools: FrozenSet[str]
    installed_models: FrozenSet[str]
    ollama_listening: bool

    def __post_init__(self):
        if (not isinstance(self.installed_tools, frozenset) or
                not isinstance(self.installed_models, frozenset) or
                not all(isinstance(x, str) and x for x in self.installed_tools | self.installed_models) or
                type(self.ollama_listening) is not bool):
            raise RoutingDenied("Malformed trusted local inventory")


@dataclass(frozen=True)
class Route:
    worker: str
    inference: str
    model: str
    base_url: str
    execution: str = "PROPOSAL_ONLY"
    estimated_cloud_usd: int = 0


APPROVED_CODE_WORKERS = ("kilo", "aider", "opencode")


def propose_local_route(
    kind: str, inventory: LocalInventory, *, model: str, preferred_worker: str | None = None
) -> Route:
    if (not isinstance(inventory, LocalInventory) or type(kind) is not str or
            (preferred_worker is not None and
             (type(preferred_worker) is not str or preferred_worker not in APPROVED_CODE_WORKERS))):
        raise RoutingDenied("Invalid route request or disallowed preferred worker")
    if (not inventory.ollama_listening or not isinstance(model, str) or
            model not in inventory.installed_models):
        raise RoutingDenied("Ollama/model unavailable: do not switch to paid provider")
    if kind == "code":
        if preferred_worker is not None:
            # Explicit choices must fail closed; never silently select another agent.
            worker = preferred_worker if preferred_worker in inventory.installed_tools else None
        else:
            worker = next((w for w in APPROVED_CODE_WORKERS if w in inventory.installed_tools), None)
    elif kind == "general":
        if preferred_worker is not None:
            raise RoutingDenied("Preferred coding worker is invalid for general tasks")
        worker = "hermes" if "hermes" in inventory.installed_tools else None
    else:
        raise RoutingDenied("Unknown task class")
    if worker is None:
        raise RoutingDenied("No approved local worker available")
    return Route(worker=worker, inference="ollama", model=model, base_url="http://127.0.0.1:11434")
