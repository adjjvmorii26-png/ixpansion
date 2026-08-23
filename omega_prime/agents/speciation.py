"""Speciation engine.

When an agent's entropy pressure exceeds a threshold or it survives
enough anomalous events, the speciation engine rolls for mutation.
A successful roll produces a new species variant with modified
behavioral parameters. Over time, this creates emergent biodiversity
shaped by the environment's selection pressures.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SpeciesGenome:
    """Behavioral parameters that define a species variant."""

    base_species: str
    aggression: float = 0.3      # 0=pacifist, 1=hyper-aggressive
    curiosity: float = 0.5       # 0=cautious, 1=recklessly exploratory
    cooperation: float = 0.5     # 0=solitary, 1=hive-mind
    entropy_tolerance: float = 0.5  # How much chaos before lockout sensitivity increases
    generation: int = 0

    def mutate(self, intensity: float = 0.2) -> "SpeciesGenome":
        """Produce a mutated offspring genome."""
        rng = random.Random()
        return SpeciesGenome(
            base_species=self.base_species,
            aggression=max(0.0, min(1.0, self.aggression + rng.gauss(0, intensity))),
            curiosity=max(0.0, min(1.0, self.curiosity + rng.gauss(0, intensity))),
            cooperation=max(0.0, min(1.0, self.cooperation + rng.gauss(0, intensity))),
            entropy_tolerance=max(0.1, min(1.0, self.entropy_tolerance + rng.gauss(0, intensity * 0.5))),
            generation=self.generation + 1,
        )

    @property
    def species_label(self) -> str:
        """Human-readable species classification based on genome."""
        if self.aggression > 0.7 and self.cooperation > 0.7:
            return f"warrior-hive.gen{self.generation}"
        elif self.aggression > 0.7:
            return f"berserker.gen{self.generation}"
        elif self.curiosity > 0.8 and self.cooperation < 0.3:
            return f"lone-explorer.gen{self.generation}"
        elif self.cooperation > 0.8:
            return f"collectivist.gen{self.generation}"
        return f"{self.base_species}.gen{self.generation}"


@dataclass
class SpeciationEvent:
    parent_id: str
    child_genome: SpeciesGenome
    trigger: str
    tick: int


class SpeciationEngine:
    MUTATION_BASE_CHANCE = 0.05   # Baseline per-tick chance
    PRESSURE_MULTIPLIER = 3.0     # How much entropy pressure boosts mutation odds

    def __init__(self) -> None:
        self._genomes: dict[str, SpeciesGenome] = {}
        self._events: list[SpeciationEvent] = []

    def register(self, agent_id: str, genome: SpeciesGenome) -> None:
        self._genomes[agent_id] = genome

    def evaluate(self, agent_id: str, entropy_pressure: float,
                 anomaly_count: int, tick: int) -> SpeciationEvent | None:
        """Roll for spontaneous mutation based on current conditions."""
        genome = self._genomes.get(agent_id)
        if not genome:
            return None

        # Mutation probability scales with pressure and anomaly exposure
        chance = (
            self.MUTATION_BASE_CHANCE
            + (entropy_pressure * self.PRESSURE_MULTIPLIER * 0.01)
            + (anomaly_count * 0.02)
        )
        chance = min(chance, 0.5)  # Cap at 50%

        if random.random() > chance:
            return None

        # Higher pressure = more dramatic mutation
        intensity = 0.1 + (entropy_pressure * 0.3)
        child_genome = genome.mutate(intensity=intensity)

        event = SpeciationEvent(
            parent_id=agent_id,
            child_genome=child_genome,
            trigger=f"pressure={round(entropy_pressure,2)} anomalies={anomaly_count}",
            tick=tick,
        )
        self._events.append(event)
        return event

    @property
    def lineage_tree(self) -> dict[str, list[str]]:
        """Map base species to their evolved descendants."""
        tree: dict[str, list[str]] = {}
        for aid, genome in self._genomes.items():
            tree.setdefault(genome.base_species, []).append(genome.species_label)
        return {k: sorted(set(v)) for k, v in tree.items()}

    @property
    def total_events(self) -> int:
        return len(self._events)

    @property
    def population_stats(self) -> dict[str, Any]:
        if not self._genomes:
            return {}
        avg_agg = sum(g.aggression for g in self._genomes.values()) / len(self._genomes)
        avg_cur = sum(g.curiosity for g in self._genomes.values()) / len(self._genomes)
        avg_coop = sum(g.cooperation for g in self._genomes.values()) / len(self._genomes)
        max_gen = max(g.generation for g in self._genomes.values())
        return {
            "population": len(self._genomes),
            "avg_aggression": round(avg_agg, 3),
            "avg_curiosity": round(avg_cur, 3),
            "avg_cooperation": round(avg_coop, 3),
            "max_generation": max_gen,
        }
