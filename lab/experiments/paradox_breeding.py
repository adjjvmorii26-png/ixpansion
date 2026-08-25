#!/usr/bin/env python3
"""Paradox Breeding Chamber — cross-pollinate paradox signatures to discover new paradoxes.

Takes two existing paradox signatures (from paradox_signatures.py) and
"breeds" them by:
1. Finding overlapping trait dimensions
2. Computing interference patterns in their cosine-similarity fingerprints
3. Producing offspring paradoxes that inherit traits from both parents

The result is a genealogy tree of paradoxes, each labeled with a
generation number and a novelty score measuring how different it is
from its parents.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ParadoxDNA:
    """The genome of a paradox — a vector of trait intensities."""
    traits: dict[str, float]
    generation: int = 0
    parent_ids: tuple[str, ...] = ()

    @property
    def genome_id(self) -> str:
        raw = json.dumps(self.traits, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    @property
    def magnitude(self) -> float:
        return math.sqrt(sum(v * v for v in self.traits.values()))


def _cosine_sim(a: dict[str, float], b: dict[str, float]) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    mag_a = math.sqrt(sum(v * v for v in a.values()))
    mag_b = math.sqrt(sum(v * v for v in b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _novelty(traits: dict[str, float], parent_a: dict[str, float], parent_b: dict[str, float]) -> float:
    """How different the child is from both parents (1 = completely novel)."""
    sim_a = _cosine_sim(traits, parent_a)
    sim_b = _cosine_sim(traits, parent_b)
    return round(1.0 - (sim_a + sim_b) / 2, 4)


@dataclass
class ParadoxChamber:
    """Breeds paradoxes from two parent signatures."""
    mutation_rate: float = 0.15
    crossover_rate: float = 0.6
    seed: int | None = None

    def __post_init__(self) -> None:
        import random
        self._rng = random.Random(self.seed)

    def breed(self, parent_a: ParadoxDNA, parent_b: ParadoxDNA) -> ParadoxDNA:
        """Produce a child paradox from two parents."""
        all_traits = set(parent_a.traits) | set(parent_b.traits)
        child_traits: dict[str, float] = {}

        for trait in all_traits:
            a_val = parent_a.traits.get(trait, 0.0)
            b_val = parent_b.traits.get(trait, 0.0)

            # Crossover: blend or take from one parent
            if self._rng.random() < self.crossover_rate:
                # Interference blend (like quantum superposition)
                alpha = self._rng.uniform(0.2, 0.8)
                blended = alpha * a_val + (1 - alpha) * b_val
            else:
                # Take the more extreme value
                blended = max(a_val, b_val) if self._rng.random() > 0.5 else min(a_val, b_val)

            # Mutation
            if self._rng.random() < self.mutation_rate:
                blended += self._rng.gauss(0, 0.2)

            child_traits[trait] = round(max(0.0, min(1.0, blended)), 4)

        gen = max(parent_a.generation, parent_b.generation) + 1
        return ParadoxDNA(
            traits=child_traits,
            generation=gen,
            parent_ids=(parent_a.genome_id, parent_b.genome_id),
        )

    def breed_lineage(
        self, seed_a: ParadoxDNA, seed_b: ParadoxDNA, generations: int = 5
    ) -> list[dict[str, Any]]:
        """Produce a multi-generation lineage of bred paradoxes."""
        lineage: list[dict[str, Any]] = []
        current_a, current_b = seed_a, seed_b

        for gen in range(generations):
            child = self.breed(current_a, current_b)
            novelty = _novelty(child.traits, current_a.traits, current_b.traits)
            lineage.append({
                "generation": child.generation,
                "genome_id": child.genome_id,
                "parent_ids": list(child.parent_ids),
                "novelty": novelty,
                "magnitude": round(child.magnitude, 4),
                "traits": child.traits,
            })
            # Evolve parents: one stays, one is replaced by child
            if gen % 2 == 0:
                current_a = child
            else:
                current_b = child

        return lineage

    def tournament(
        self, population: list[ParadoxDNA], rounds: int = 3
    ) -> ParadoxDNA:
        """Select the most novel paradox through tournament selection."""
        if len(population) < 2:
            return population[0] if population else ParadoxDNA(traits={})

        best = population[0]
        for _ in range(rounds):
            a = self._rng.choice(population)
            b = self._rng.choice(population)
            # Novelty against the rest of the population
            others = [p for p in population if p.genome_id not in (a.genome_id, b.genome_id)]
            if others:
                avg_a = sum(_cosine_sim(a.traits, o.traits) for o in others) / len(others)
                avg_b = sum(_cosine_sim(b.traits, o.traits) for o in others) / len(others)
            else:
                avg_a, avg_b = a.magnitude, b.magnitude
            # Lower average similarity = more novel = wins
            if avg_a < avg_b:
                best = a if _cosine_sim(best.traits, a.traits) < _cosine_sim(best.traits, b.traits) else b

        return best


# ── Seed paradoxes representing archetypes ──

SEED_TRUTH_LOOP = ParadoxDNA(traits={
    "self_reference": 1.0, "negation": 0.8, "temporal": 0.3,
    "identity": 0.6, "entropy": 0.5, "recursion": 0.9,
})

SEED_UNKNOWABLE = ParadoxDNA(traits={
    "self_reference": 0.7, "negation": 1.0, "temporal": 0.5,
    "identity": 0.3, "entropy": 0.8, "recursion": 0.4,
})

SEED_BOOTSTRAP = ParadoxDNA(traits={
    "self_reference": 0.9, "negation": 0.2, "temporal": 1.0,
    "identity": 0.5, "entropy": 0.3, "recursion": 0.7,
})

SEED_CROCODILE = ParadoxDNA(traits={
    "self_reference": 0.5, "negation": 0.6, "temporal": 0.8,
    "identity": 1.0, "entropy": 0.4, "recursion": 0.5,
})


def demo() -> dict[str, Any]:
    chamber = ParadoxChamber(seed=42)
    lineage = chamber.breed_lineage(SEED_TRUTH_LOOP, SEED_UNKNOWABLE, generations=8)

    # Tournament across all lineage members
    population = [ParadoxDNA(traits=entry["traits"], generation=entry["generation"]) for entry in lineage]
    champion = chamber.tournament(population, rounds=5)

    return {
        "lineage_length": len(lineage),
        "champion_id": champion.genome_id,
        "champion_generation": champion.generation,
        "champion_magnitude": round(champion.magnitude, 4),
        "lineage": lineage,
    }


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
