"""Immutable truths the engine obeys. These cannot be overridden."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class Axiom:
    axiom_id: str
    statement: str
    validator: Callable[[Any], bool]
    severity: str  # "fatal" | "warn"


AXIOMS: tuple[Axiom, ...] = (
    Axiom(
        "A1",
        "Entropy is conserved; it may transform but never vanish.",
        lambda system_state: system_state.get("total_entropy", 0) >= 0,
        "fatal",
    ),
    Axiom(
        "A2",
        "No agent may occupy two positions simultaneously in Euclidean space.",
        lambda agent: len(agent.get("positions", [])) <= 1 or agent.get("dimension") != "euclid",
        "warn",
    ),
    Axiom(
        "A3",
        "Every pulse must produce at least one observable state change.",
        lambda tick_result: tick_result.get("mutations", 0) > 0,
        "warn",
    ),
    Axiom(
        "A4",
        "The observer effect: measurement collapses superposition.",
        lambda obs: not (obs.get("is_superposed") and obs.get("is_measured")),
        "fatal",
    ),
    Axiom(
        "A5",
        "Recursion must terminate or be explicitly bounded.",
        lambda call_stack: call_stack.get("depth", 0) < call_stack.get("max_depth", float("inf")),
        "fatal",
    ),
)


def enforce(axiom_id: str, context: Any) -> bool:
    """Validate a context against a specific axiom."""
    for axiom in AXIOMS:
        if axiom.axiom_id == axiom_id:
            return axiom.validator(context)
    raise KeyError(f"Unknown axiom: {axiom_id}")


def enforce_all(context_map: dict[str, Any]) -> dict[str, bool]:
    """Enforce all axioms against their respective contexts."""
    results = {}
    for axiom in AXIOMS:
        ctx = context_map.get(axiom.axiom_id)
        if ctx is not None:
            try:
                results[axiom.axiom_id] = axiom.validator(ctx)
            except Exception:
                results[axiom.axiom_id] = False
    return results
