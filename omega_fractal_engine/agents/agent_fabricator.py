"""Creates new agent species dynamically based on environmental pressure."""
from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentTemplate:
    species: str
    category: str  # primal, synthetic, spectral, overseer
    genome: dict[str, Any] = field(default_factory=dict)
    generation: int = 0

    @property
    def label(self) -> str:
        return f"{self.species}.gen{self.generation}.{self.category}"


class AgentFabricator:
    CATEGORIES = ["primal", "synthetic", "spectral", "overseer"]

    def __init__(self) -> None:
        self._templates: dict[str, AgentTemplate] = {}
        self._spawn_count: dict[str, int] = defaultdict(int)

    def forge(self, base_species: str, category: str,
              mutations: dict[str, Any] | None = None) -> AgentTemplate:
        """Create a new agent template with optional genetic modifications."""
        gen = self._spawn_count[base_species]
        genome = {
            "aggression": random.uniform(0.1, 0.9),
            "curiosity": random.uniform(0.1, 0.9),
            "cooperation": random.uniform(0.1, 0.9),
            "entropy_tolerance": random.uniform(0.2, 0.8),
        }
        if mutations:
            genome.update(mutations)

        template = AgentTemplate(
            species=base_species,
            category=category,
            genome=genome,
            generation=gen + 1,
        )
        key = f"{base_species}_{gen}"
        self._templates[key] = template
        self._spawn_count[base_species] += 1
        return template

    def hybridize(self, parent_a: AgentTemplate, parent_b: AgentTemplate) -> AgentTemplate:
        """Merge two agent genomes into a hybrid species."""
        child_genome = {}
        for key in set(parent_a.genome) | set(parent_b.genome):
            va = parent_a.genome.get(key, random.random())
            vb = parent_b.genome.get(key, random.random())
            # Blend with slight mutation
            child_genome[key] = max(0.0, min(1.0, (va + vb) / 2 + random.gauss(0, 0.1)))

        hybrid_name = f"{parent_a.species[:4]}-{parent_b.species[:4]}"
        return self.forge(hybrid_name, parent_a.category, mutations=child_genome)

    @property
    def catalog(self) -> list[dict[str, Any]]:
        return [
            {"label": t.label, "genome": {k: round(v, 3) for k, v in t.genome.items()}}
            for t in self._templates.values()
        ]
