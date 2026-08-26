"""Wave 125 — Genetic Code Engine.

Encodes system configurations as genetic sequences — allowing crossover,
mutation, and selection to evolve optimal configurations through
simulated natural selection.
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List, Optional


class Genome:
    """A genetic sequence encoding system configuration."""

    BASES = ["A", "C", "G", "T"]

    def __init__(self, sequence: str, name: str = ""):
        self.sequence = sequence
        self.name = name or hashlib.sha256(sequence.encode()).hexdigest()[:8]
        self.fitness = 0.0
        self.created = time.time()
        self.generation = 0

    def decode(self) -> Dict[str, Any]:
        gene_length = max(1, len(self.sequence) // 4)
        return {
            "complexity": self.sequence.count("G") / max(len(self.sequence), 1),
            "stability": self.sequence.count("A") / max(len(self.sequence), 1),
            "adaptability": self.sequence.count("T") / max(len(self.sequence), 1),
            "efficiency": self.sequence.count("C") / max(len(self.sequence), 1),
        }

    def crossover(self, other: "Genome") -> "Genome":
        mid = len(self.sequence) // 2
        child_seq = self.sequence[:mid] + other.sequence[mid:]
        child = Genome(child_seq, f"child_{self.name}_{other.name}")
        child.generation = max(self.generation, other.generation) + 1
        return child

    def mutate(self, rate: float = 0.05) -> "Genome":
        seq = list(self.sequence)
        for i in range(len(seq)):
            if random.random() < rate:
                seq[i] = random.choice(self.BASES)
        mutant = Genome("".join(seq), f"mutant_{self.name}")
        mutant.generation = self.generation + 1
        return mutant

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "length": len(self.sequence),
                "generation": self.generation, "fitness": round(self.fitness, 4)}


class GeneticCodeEngine:
    """Evolves configurations through genetic algorithms."""

    def __init__(self):
        self._population: List[Genome] = []
        self._evolution_cycles = 0

    def seed(self, sequence: str, name: str = "") -> Genome:
        genome = Genome(sequence, name)
        self._population.append(genome)
        return genome

    def evaluate_fitness(self, genome: Genome, metric_fn=None) -> float:
        if metric_fn:
            genome.fitness = metric_fn(genome)
        else:
            genes = genome.decode()
            genome.fitness = sum(genes.values()) / len(genes)
        return genome.fitness

    def evolve(self, parent_a: Genome, parent_b: Genome) -> Genome:
        child = parent_a.crossover(parent_b)
        self._population.append(child)
        self._evolution_cycles += 1
        return child

    def select_fittest(self, n: int = 1) -> List[Genome]:
        return sorted(self._population, key=lambda g: g.fitness, reverse=True)[:n]

    def status(self) -> Dict[str, Any]:
        avg_fitness = sum(g.fitness for g in self._population) / max(len(self._population), 1)
        return {"population": len(self._population), "avg_fitness": round(avg_fitness, 4),
                "evolution_cycles": self._evolution_cycles}
