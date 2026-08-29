"""Wave 132 — Workforce Genetics.

Workers are born from a gene pool: traits like curiosity, diligence,
and risk-tolerance are inherited from parent workers with mutation.
Selecting the best-performing parents evolves the workforce over
generations.
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List

TRAITS = ["curiosity", "diligence", "risk_tolerance", "collaboration", "entropy_affinity"]


class Genome:
    """A worker's trait vector."""

    def __init__(self, traits: Dict[str, float]):
        self.traits = {t: max(0.0, min(1.0, traits.get(t, 0.5))) for t in TRAITS}

    def fertility(self) -> float:
        return round(sum(self.traits.values()) / len(self.traits), 4)

    def to_dict(self) -> Dict[str, float]:
        return dict(self.traits)


class WorkforceGenetics:
    """Evolves workers through inheritance and mutation."""

    def __init__(self, seed: int = 0):
        self._rng = random.Random(seed)
        self._generations: Dict[int, List[str]] = {}
        self._genomes: Dict[str, Genome] = {}
        self._mutation_count = 0

    def spawn(self, name: str, traits: Dict[str, float]) -> Genome:
        genome = Genome(traits)
        self._genomes[name] = genome
        self._generations.setdefault(0, []).append(name)
        return genome

    def breed(self, child: str, parent_a: str, parent_b: str,
              generation: int = 1, mutation_rate: float = 0.1) -> Genome:
        a = self._genomes.get(parent_a)
        b = self._genomes.get(parent_b)
        if a is None or b is None:
            return self.spawn(child, {})
        blended: Dict[str, float] = {}
        for t in TRAITS:
            value = (a.traits[t] + b.traits[t]) / 2.0
            if self._rng.random() < mutation_rate:
                value += self._rng.uniform(-0.2, 0.2)
                self._mutation_count += 1
            blended[t] = max(0.0, min(1.0, value))
        self._genomes[child] = Genome(blended)
        self._generations.setdefault(generation, []).append(child)
        return self._genomes[child]

    def best_parents(self, top: int = 2) -> List[str]:
        ranked = sorted(self._genomes, key=lambda n: self._genomes[n].fertility(), reverse=True)
        return ranked[:top]

    def status(self) -> Dict[str, Any]:
        return {"workers": len(self._genomes),
                "generations": len(self._generations),
                "mutations": self._mutation_count}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    genetics = WorkforceGenetics()
    return {"status": "active", "module": "workforce_genetics",
            **genetics.status()}
