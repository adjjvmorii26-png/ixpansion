"""Wave 121 — Eigenstate Resonator.

Finds stable resonant states (eigenstates) that persist across
perturbations — configurations that, when disrupted, naturally
relax back to the same state. The system discovers its own attractors.
"""
from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Optional


class Eigenstate:
    """A stable resonant state."""

    def __init__(self, name: str, signature: List[float]):
        self.name = name
        self.signature = signature
        self.created = time.time()
        self.stability = 1.0
        self.perturbation_count = 0
        self.recovery_count = 0

    def perturb(self, magnitude: float) -> float:
        self.perturbation_count += 1
        self.stability = max(0.0, self.stability - magnitude * 0.1)
        return self.stability

    def recover(self) -> float:
        self.recovery_count += 1
        self.stability = min(1.0, self.stability + 0.05)
        return self.stability

    @property
    def resilience(self) -> float:
        if self.perturbation_count == 0:
            return 1.0
        return self.recovery_count / self.perturbation_count

    def distance_to(self, other: "Eigenstate") -> float:
        n = min(len(self.signature), len(other.signature))
        return math.sqrt(sum((self.signature[i] - other.signature[i]) ** 2 for i in range(n)))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "stability": round(self.stability, 4),
            "resilience": round(self.resilience, 4),
            "perturbations": self.perturbation_count,
            "recoveries": self.recovery_count,
        }


class EigenstateResonator:
    """Discovers and tracks eigenstates in the system."""

    def __init__(self):
        self._states: List[Eigenstate] = []
        self._discovery_log: List[str] = []

    def register(self, name: str, signature: List[float]) -> Eigenstate:
        state = Eigenstate(name, signature)
        self._states.append(state)
        self._discovery_log.append(f"Discovered eigenstate: {name}")
        return state

    def test_stability(self, state: Eigenstate, perturbations: int = 5) -> float:
        for _ in range(perturbations):
            state.perturb(0.3)
            state.recover()
        return state.stability

    def find_nearest(self, target: Eigenstate) -> Optional[Eigenstate]:
        if not self._states:
            return None
        return min(self._states, key=lambda s: s.distance_to(target) if s != target else float("inf"))

    def get_states(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self._states]

    def status(self) -> Dict[str, Any]:
        avg_stability = (
            sum(s.stability for s in self._states) / len(self._states)
            if self._states else 0.0
        )
        return {
            "total_states": len(self._states),
            "avg_stability": round(avg_stability, 4),
            "total_perturbations": sum(s.perturbation_count for s in self._states),
        }
