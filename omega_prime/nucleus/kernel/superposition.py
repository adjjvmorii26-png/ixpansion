"""Quantum action superposition.

An agent can defer decision-making by committing to multiple possible
actions with assigned amplitudes. The system holds all branches open
until the next pulse, at which point it collapses to exactly one
action based on amplitude-weighted random selection.

This is useful when an agent faces high uncertainty and wants to
"hedge" its behavior.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Branch:
    action: dict[str, Any]
    amplitude: float

    @property
    def probability(self) -> float:
        return self.amplitude ** 2


class SuperpositionState:
    def __init__(self) -> None:
        self._branches: list[Branch] = []
        self._collapsed: dict[str, Any] | None = None

    @property
    def is_superposed(self) -> bool:
        return len(self._branches) > 1 and self._collapsed is None

    @property
    def branch_count(self) -> int:
        return len(self._branches)

    def add_branch(self, action: dict[str, Any], amplitude: float) -> None:
        """Add a branch. Amplitude will be normalized at collapse time."""
        if not (0.0 < amplitude <= 1.0):
            raise ValueError(f"Amplitude must be in (0,1], got {amplitude}")
        self._branches.append(Branch(action=action, amplitude=amplitude))

    def collapse(self, rng_seed: int | None = None) -> dict[str, Any]:
        """Collapse superposition to a single action."""
        if not self._branches:
            return {}
        if len(self._branches) == 1:
            self._collapsed = self._branches[0].action
            return self._collapsed

        rng = random.Random(rng_seed) if rng_seed else random
        total_amplitude_sq = sum(b.probability for b in self._branches)
        if total_amplitude_sq == 0:
            # Uniform collapse
            chosen = rng.choice(self._branches)
        else:
            roll = rng.uniform(0, total_amplitude_sq)
            cumulative = 0.0
            chosen = self._branches[-1]  # fallback
            for branch in self._branches:
                cumulative += branch.probability
                if roll <= cumulative:
                    chosen = branch
                    break

        self._collapsed = chosen.action
        return self._collapsed

    def reset(self) -> None:
        self._branches.clear()
        self._collapsed = None

    def probabilities(self) -> list[dict[str, Any]]:
        total = sum(b.probability for b in self._branches)
        if total == 0:
            total = 1.0
        return [
            {"action": b.action.get("intent", "?"), "p": round(b.probability / total, 4)}
            for b in self._branches
        ]
