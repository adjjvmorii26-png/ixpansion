"""Handles contradictory states — the engine's self-awareness about its own logic."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ResolutionStrategy(Enum):
    QUANTUM_SUPERPOSITION = auto()   # Hold both truths simultaneously
    TEMPORAL_SEPARATION = auto()     # Truth A before tick N, truth B after
    CONTEXT_PARTITION = auto()       # Both true in different scopes
    SACRIFICE_WEAKER = auto()        # Discard the less-supported claim
    EMERGENT_SYNTHESIS = auto()      # Generate a third truth from the tension


@dataclass
class Paradox:
    paradox_id: int
    claim_a: str
    claim_b: str
    support_a: float  # Evidence weight for A
    support_b: float  # Evidence weight for B
    strategy: ResolutionStrategy | None = None

    @property
    def is_resolved(self) -> bool:
        return self.strategy is not None


class ParadoxSolver:
    def __init__(self) -> None:
        self._paradoxes: list[Paradox] = []
        self._counter = 0
        self._resolution_log: list[dict[str, Any]] = []

    def detect(self, claim_a: str, claim_b: str,
               support_a: float, support_b: float) -> Paradox:
        """Register a detected contradiction."""
        self._counter += 1
        p = Paradox(
            paradox_id=self._counter,
            claim_a=claim_a, claim_b=claim_b,
            support_a=support_a, support_b=support_b,
        )
        self._paradoxes.append(p)
        return p

    def resolve(self, paradox: Paradox) -> dict[str, Any]:
        """Choose and apply a resolution strategy based on context."""
        ratio = paradox.support_a / max(paradox.support_a + paradox.support_b, 0.001)
        confidence_gap = abs(paradox.support_a - paradox.support_b)

        if confidence_gap > 0.7:
            # One claim clearly dominates
            strategy = ResolutionStrategy.SACRIFICE_WEAKER
            winner = paradox.claim_a if paradox.support_a > paradox.support_b else paradox.claim_b
            outcome = winner
        elif abs(ratio - 0.5) < 0.05:
            # Perfectly balanced — superposition
            strategy = ResolutionStrategy.QUANTUM_SUPERPOSITION
            outcome = f"SUPERPOSED({paradox.claim_a} ∧ {paradox.claim_b})"
        elif 0.3 < ratio < 0.7:
            # Claims are roughly balanced — try synthesis
            strategy = ResolutionStrategy.EMERGENT_SYNTHESIS
            outcome = f"SYNTHESIS({paradox.claim_a} ⊗ {paradox.claim_b})"
        else:
            strategy = ResolutionStrategy.TEMPORAL_SEPARATION
            first = paradox.claim_a if paradox.support_a > paradox.support_b else paradox.claim_b
            second = paradox.claim_b if first == paradox.claim_a else paradox.claim_a
            outcome = f"SEQUENCE({first} → {second})"

        paradox.strategy = strategy
        result = {
            "paradox_id": paradox.paradox_id,
            "strategy": strategy.name,
            "outcome": outcome,
            "confidence": round(max(paradox.support_a, paradox.support_b), 4),
        }
        self._resolution_log.append(result)
        return result

    @property
    def unresolved_count(self) -> int:
        return sum(1 for p in self._paradoxes if not p.is_resolved)

    @property
    def stats(self) -> dict[str, Any]:
        strategies_used: dict[str, int] = {}
        for entry in self._resolution_log:
            s = entry["strategy"]
            strategies_used[s] = strategies_used.get(s, 0) + 1
        return {
            "total_paradoxes": len(self._paradoxes),
            "resolved": len(self._resolution_log),
            "unresolved": self.unresolved_count,
            "strategies_used": strategies_used,
        }
