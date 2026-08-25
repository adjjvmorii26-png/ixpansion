#!/usr/bin/env python3
"""Cordyceps Mutation Engine — consent-bounded trait propagation.

Bridges cordyceps (consent-bounded spread) + speciation + mutation_engine
to model how new traits propagate through a population. Traits can only
spread to agents that consent to receive them. Agents that refuse gain
"immunity memory" — they can't be offered the same trait again.

This creates evolutionary pressure: traits that spread widely are
popular; traits that encounter mass refusal are rejected by the culture.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Trait:
    trait_id: str
    name: str
    mutation_strength: float
    description: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "trait_id": self.trait_id,
            "name": self.name,
            "mutation_strength": round(self.mutation_strength, 4),
        }


@dataclass
class MutantAgent:
    agent_id: str
    species: str
    traits: dict[str, float] = field(default_factory=dict)
    consent_history: set[str] = field(default_factory=set)
    immunity: set[str] = field(default_factory=set)
    fitness: float = 1.0

    def consider(self, trait: Trait, social_pressure: float = 0.5) -> bool:
        """Decide whether to accept a trait based on fitness and social pressure."""
        if trait.trait_id in self.immunity:
            return False
        # Higher fitness = more selective; lower fitness = more open
        openness = 1.0 - self.fitness * 0.5
        consent_probability = openness * social_pressure + 0.1
        return random.random() < consent_probability

    def accept_trait(self, trait: Trait) -> None:
        self.traits[trait.name] = self.traits.get(trait.name, 0.0) + trait.mutation_strength
        self.consent_history.add(trait.trait_id)

    def refuse_trait(self, trait: Trait) -> None:
        self.immunity.add(trait.trait_id)

    def update_fitness(self) -> None:
        """Fitness depends on trait diversity and immunity breadth."""
        trait_diversity = len(self.traits) / 10.0
        immunity_breadth = len(self.immunity) / 20.0
        self.fitness = min(2.0, max(0.1, 0.5 + trait_diversity * 0.3 + immunity_breadth * 0.2))


@dataclass
class CordycepsMutationEngine:
    """Consent-bounded trait propagation engine."""
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._agents: dict[str, MutantAgent] = {}
        self._traits: dict[str, Trait] = {}
        self._propagation_log: list[dict[str, Any]] = []
        self._tick = 0

    def add_agent(self, agent_id: str, species: str) -> MutantAgent:
        agent = MutantAgent(agent_id=agent_id, species=species)
        self._agents[agent_id] = agent
        return agent

    def create_trait(self, name: str, strength: float, description: str = "") -> Trait:
        tid = hashlib.sha256(f"{name}:{self._tick}".encode()).hexdigest()[:12]
        trait = Trait(trait_id=tid, name=name, mutation_strength=strength, description=description)
        self._traits[tid] = trait
        return trait

    def propagate_trait(self, trait: Trait, source_id: str,
                        social_pressure: float = 0.5) -> dict[str, Any]:
        """Propagate a trait from a source agent through the population."""
        source = self._agents.get(source_id)
        if not source:
            return {"status": "unknown_source"}

        accepted = 0
        refused = 0
        immune = 0

        for agent_id, agent in self._agents.items():
            if agent_id == source_id:
                continue
            if trait.trait_id in agent.immunity:
                immune += 1
                continue

            if agent.consider(trait, social_pressure):
                agent.accept_trait(trait)
                accepted += 1
            else:
                agent.refuse_trait(trait)
                refused += 1

        result = {
            "tick": self._tick,
            "trait": trait.name,
            "source": source_id,
            "accepted": accepted,
            "refused": refused,
            "immune": immune,
            "total_agents": len(self._agents),
        }
        self._propagation_log.append(result)
        return result

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        for agent in self._agents.values():
            agent.update_fitness()
        return {"tick": self._tick, "agents": len(self._agents)}

    def population_census(self) -> dict[str, Any]:
        species_dist = defaultdict(int)
        trait_popularity: dict[str, int] = defaultdict(int)
        fitness_scores = []

        for agent in self._agents.values():
            species_dist[agent.species] += 1
            for trait_name in agent.traits:
                trait_popularity[trait_name] += 1
            fitness_scores.append(agent.fitness)

        mean_fitness = sum(fitness_scores) / max(1, len(fitness_scores))
        return {
            "total_agents": len(self._agents),
            "species_distribution": dict(species_dist),
            "trait_popularity": dict(trait_popularity),
            "mean_fitness": round(mean_fitness, 4),
            "total_propagations": len(self._propagation_log),
        }


def demo() -> dict[str, Any]:
    engine = CordycepsMutationEngine(seed=42)

    # Create population
    species = ["sentinel", "architect", "wanderer"]
    for i in range(20):
        engine.add_agent(f"agent-{i}", species[i % 3])

    # Create traits and propagate
    traits = [
        engine.create_trait("night_vision", 0.3, "See in darkness"),
        engine.create_trait("echo_location", 0.5, "Navigate by sound"),
        engine.create_trait("chromatic_shift", 0.2, "Change color"),
    ]

    propagation_results = []
    for trait in traits:
        source = f"agent-{engine._rng.randint(0, 19)}"
        engine.tick()
        result = engine.propagate_trait(trait, source, social_pressure=0.6)
        propagation_results.append(result)

    return {
        "propagation_results": propagation_results,
        "census": engine.population_census(),
    }


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
