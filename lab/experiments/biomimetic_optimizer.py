from __future__ import annotations
"""Biomimetic Optimizer — optimizes by mimicking biological strategies.

Uses ant colony optimization, swarm intelligence, and evolutionary
strategies to find optimal configurations for system parameters.
"""
import math
import random
import json
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Tuple

@dataclass
class Ant:
    position: List[float]
    fitness: float = 0.0
    path: List[int] = field(default_factory=list)

class BiomimeticOptimizer:
    def __init__(self, dimensions: int = 5, pop_size: int = 20, seed: int = 42):
        self.rng = random.Random(seed)
        self.dimensions = dimensions
        self.pop_size = pop_size
        self.pheromone: List[List[float]] = [[0.0] * 10 for _ in range(dimensions)]
        self.best_solution: List[float] = []
        self.best_fitness: float = float("inf")
        self.history: List[Dict] = []

    def _ackley(self, x: List[float]) -> float:
        n = len(x)
        sum1 = sum(xi ** 2 for xi in x)
        sum2 = sum(math.cos(2 * math.pi * xi) for xi in x)
        return -20 * math.exp(-0.2 * math.sqrt(sum1 / n)) - math.exp(sum2 / n) + 20 + math.e

    def _rastrigin(self, x: List[float]) -> float:
        return 10 * len(x) + sum(xi ** 2 - 10 * math.cos(2 * math.pi * xi) for xi in x)

    def optimize(self, objective: str = "ackley", iterations: int = 50) -> List[Dict]:
        func = self._ackley if objective == "ackley" else self._rastrigin
        ants = [Ant(position=[self.rng.uniform(-5, 5) for _ in range(self.dimensions)])
                for _ in range(self.pop_size)]

        for it in range(iterations):
            for ant in ants:
                ant.fitness = func(ant.position)
                if ant.fitness < self.best_fitness:
                    self.best_fitness = ant.fitness
                    self.best_solution = ant.position.copy()

            for i in range(self.dimensions):
                for j in range(10):
                    self.pheromone[i][j] *= 0.9
                best_bin = int((self.best_solution[i] + 5) / 10 * 9)
                best_bin = max(0, min(9, best_bin))
                self.pheromone[i][best_bin] += 1.0 / (1.0 + self.best_fitness)

            for ant in ants:
                for i in range(self.dimensions):
                    if self.rng.random() < 0.3:
                        ant.position[i] = self.best_solution[i] + self.rng.gauss(0, 0.5)
                    else:
                        total = sum(self.pheromone[i])
                        if total > 0:
                            probabilities = [p / total for p in self.pheromone[i]]
                            chosen_bin = self.rng.choices(range(10), weights=probabilities, k=1)[0]
                            ant.position[i] = (chosen_bin / 9) * 10 - 5
                        ant.position[i] += self.rng.gauss(0, 0.2)
                    ant.position[i] = max(-5, min(5, ant.position[i]))

            self.history.append({
                "iteration": it, "best_fitness": round(self.best_fitness, 6),
                "avg_fitness": round(sum(a.fitness for a in ants) / len(ants), 6),
            })
        return self.history


def demo():
    opt = BiomimeticOptimizer(dimensions=3, pop_size=15, seed=42)
    print("=== Biomimetic Optimizer ===")
    history = opt.optimize(objective="ackley", iterations=30)
    print(f"  Best fitness: {opt.best_fitness:.6f}")
    print(f"  Best solution: {[round(x, 4) for x in opt.best_solution]}")
    print(f"  Converged in {len(history)} iterations")
    return {"best_fitness": opt.best_fitness, "iterations": len(history)}


if __name__ == "__main__":
    demo()
