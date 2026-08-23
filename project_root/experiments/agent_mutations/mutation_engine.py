"""Agent mutation engine — applies random mutations to agent traits."""
from __future__ import annotations

import random
from typing import Any


class MutationEngine:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def mutate_trait(self, traits: dict[str, float],
                     key: str, intensity: float = 0.2) -> float:
        old = traits.get(key, 0.5)
        new = max(0.0, min(1.0, old + self._rng.gauss(0, intensity)))
        traits[key] = round(new, 4)
        return traits[key]

    def mutate_all(self, traits: dict[str, float], probability: float = 0.3,
                   intensity: float = 0.15) -> dict[str, float]:
        for key in list(traits.keys()):
            if self._rng.random() < probability:
                self.mutate_trait(traits, key, intensity)
        return traits

    def point_mutation(self, genome: dict[str, Any]) -> dict[str, Any]:
        """Change exactly one value randomly."""
        if not genome:
            return genome
        key = self._rng.choice(list(genome.keys()))
        val = genome[key]
        if isinstance(val, (int, float)):
            genome[key] = round(max(0, min(1, val + self._rng.gauss(0, 0.2))), 4)
        elif isinstance(val, str):
            pos = self._rng.randint(0, len(val)-1) if val else 0
            genome[key] = val[:pos] + self._rng.choice("acgt") + val[pos+1:]
        return genome
