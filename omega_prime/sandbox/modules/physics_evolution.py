"""Physics evolution engine — natural selection for universal constants.

The sandbox's physical constants (gravity, friction, time flow) are not
fixed — they evolve across generations. Each generation runs a batch of
simulation pulses. Constants that produce high agent engagement, diverse
actions, and low stagnation scores are selected and mutated for the next
generation.

Over time, the universe discovers its own optimal physics.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PhysicsGenome:
    """A set of tunable physical constants."""

    gravity: float = -9.81
    friction: float = 0.98
    time_dilation: float = 1.0
    collision_elasticity: float = 0.5
    max_velocity: float = 100.0

    def to_dict(self) -> dict[str, float]:
        return {
            "gravity": round(self.gravity, 4),
            "friction": round(self.friction, 4),
            "time_dilation": round(self.time_dilation, 4),
            "collision_elasticity": round(self.collision_elasticity, 4),
            "max_velocity": round(self.max_velocity, 2),
        }

    def mutate(self, intensity: float = 0.1, rng: random.Random | None = None) -> "PhysicsGenome":
        r = rng or random
        return PhysicsGenome(
            gravity=self.gravity + r.gauss(0, abs(self.gravity) * intensity),
            friction=max(0.5, min(1.0, self.friction + r.gauss(0, intensity * 0.05))),
            time_dilation=max(0.1, min(10.0, self.time_dilation + r.gauss(0, intensity * 0.3))),
            collision_elasticity=max(0.0, min(1.0, self.collision_elasticity + r.gauss(0, intensity * 0.1))),
            max_velocity=max(10.0, min(500.0, self.max_velocity + r.gauss(0, self.max_velocity * intensity * 0.2))),
        )

    @classmethod
    def crossover(cls, a: "PhysicsGenome", b: "PhysicsGenome",
                  bias: float = 0.5, rng: random.Random | None = None) -> "PhysicsGenome":
        r = rng or random
        return cls(
            gravity=a.gravity * (1 - bias) + b.gravity * bias,
            friction=a.friction * (1 - bias) + b.friction * bias,
            time_dilation=a.time_dilation * (1 - bias) + b.time_dilation * bias,
            collision_elasticity=a.collision_elasticity * (1 - bias) + b.collision_elasticity * bias,
            max_velocity=a.max_velocity * (1 - bias) + b.max_velocity * bias,
        )


@dataclass
class GenerationResult:
    generation: int
    genome: PhysicsGenome
    fitness_score: float
    metrics: dict[str, float] = field(default_factory=dict)


class FitnessEvaluator:
    """Scores a physics genome based on emergent behavior quality."""

    def evaluate(self, metrics: dict[str, float]) -> float:
        """
        Metrics:
          interaction_rate   — fraction of agents that acted (higher = better)
          action_diversity   — unique action types / total possible (higher = better)
          stagnation_rate    — fraction doing nothing (lower = better)
          energy_efficiency  — useful work / entropy spent (higher = better)
        """
        interaction = min(1.0, metrics.get("interaction_rate", 0))
        diversity = min(1.0, metrics.get("action_diversity", 0))
        stagnation = max(0.0, metrics.get("stagnation_rate", 1))  # Invert: lower is better
        efficiency = min(1.0, metrics.get("energy_efficiency", 0))

        score = (
            interaction * 0.30 +
            diversity * 0.25 +
            (1.0 - stagnation) * 0.25 +
            efficiency * 0.20
        )
        return round(max(0.0, min(1.0, score)), 6)


class PhysicsEvolutionEngine:
    ELITE_FRACTION = 0.2     # Top 20% survive unchanged
    MUTATION_RATE = 0.15     # Per-gene mutation probability
    POPULATION_SIZE = 12

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._evaluator = FitnessEvaluator()
        self._population: list[tuple[PhysicsGenome, float]] = []
        self._generation = 0
        self._history: list[GenerationResult] = []

    def initialize(self) -> list[PhysicsGenome]:
        """Generate initial random population."""
        population = []
        for _ in range(self.POPULATION_SIZE):
            genome = PhysicsGenome(
                gravity=self._rng.uniform(-50, 0),
                friction=self._rng.uniform(0.7, 1.0),
                time_dilation=self._rng.uniform(0.3, 3.0),
                collision_elasticity=self._rng.uniform(0.1, 0.9),
                max_velocity=self._rng.uniform(20, 200),
            )
            population.append(genome)
        return population

    def submit_generation(self, scored_genomes: list[tuple[PhysicsGenome, dict[str, float]]]) -> dict[str, Any]:
        """Submit evaluation results for current population; evolve next gen."""
        self._generation += 1
        scored = [
            (genome, self._evaluator.evaluate(metrics), metrics)
            for genome, metrics in scored_genomes
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Record history
        best_genome, best_fitness, best_metrics = scored[0]
        self._history.append(GenerationResult(
            generation=self._generation, genome=best_genome,
            fitness_score=best_fitness, metrics=best_metrics,
        ))

        # Select elites
        elite_count = max(1, int(len(scored) * self.ELITE_FRACTION))
        elites = [g for g, _, _ in scored[:elite_count]]

        # Breed next generation
        offspring = []
        while len(offspring) < self.POPULATION_SIZE - len(elites):
            parent_a = self._tournament_select(scored)
            parent_b = self._tournament_select(scored)
            child = PhysicsGenome.crossover(parent_a, parent_b, bias=self._rng.uniform(0.3, 0.7), rng=self._rng)

            # Mutate
            child = self._maybe_mutate(child)
            offspring.append(child)

        self._population = [(g, 0.0) for g in elites + offspring]
        return {
            "generation": self._generation,
            "best_fitness": best_fitness,
            "best_constants": best_genome.to_dict(),
            "avg_fitness": round(sum(f for _, f, _ in scored) / len(scored), 6),
            "population_size": len(self._population),
        }

    def _tournament_select(self, scored: list[tuple[PhysicsGenome, float, dict]],
                           tournament_size: int = 3) -> PhysicsGenome:
        contestants = self._rng.sample(scored, min(tournament_size, len(scored)))
        winner = max(contestants, key=lambda x: x[1])
        return winner[0]

    def _maybe_mutate(self, genome: PhysicsGenome) -> PhysicsGenome:
        if self._rng.random() < self.MUTATION_RATE:
            return genome.mutate(intensity=self._rng.uniform(0.05, 0.2), rng=self._rng)
        return genome

    @property
    def generation_count(self) -> int:
        return self._generation

    @property
    def best_ever(self) -> dict[str, Any] | None:
        if not self._history:
            return None
        best = max(self._history, key=lambda h: h.fitness_score)
        return {
            "generation": best.generation,
            "fitness": best.fitness_score,
            "constants": best.genome.to_dict(),
        }
