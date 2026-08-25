"""Agent Ecology — Simulates predator-prey dynamics between agent species.

Models the codebase's agent ecosystem as a food chain where different
agent types compete for resources (CPU, memory, attention).
"""
from __future__ import annotations
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Species:
    def __init__(self, name: str, population: int, energy: float, reproduction_rate: float, predation_rate: float):
        self.name = name
        self.population = population
        self.energy = energy
        self.reproduction_rate = reproduction_rate
        self.predation_rate = predation_rate
        self.history: list[int] = [population]

    def step(self, prey_population: int, predator_population: int):
        # Lotka-Volterra inspired dynamics
        growth = self.reproduction_rate * self.population * (1 - self.population / 100)
        predation_loss = self.predation_rate * self.population * predator_population * 0.001
        prey_gain = self.predation_rate * prey_population * self.population * 0.001

        self.population = max(0, int(self.population + growth - predation_loss + prey_gain))
        self.energy = min(1.0, self.energy + (prey_gain - predation_loss) * 0.01)
        self.history.append(self.population)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "population": self.population,
            "energy": round(self.energy, 4),
            "trend": "growing" if len(self.history) > 1 and self.history[-1] > self.history[-2] else "declining",
        }


class Ecology:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.species: list[Species] = []
        self.tick_count = 0

    def add_species(self, name, pop, energy, repro, predation):
        self.species.append(Species(name, pop, energy, repro, predation))

    def tick(self):
        self.tick_count += 1
        for i, sp in enumerate(self.species):
            prey = self.species[(i + 1) % len(self.species)].population if len(self.species) > 1 else 0
            pred = self.species[(i - 1) % len(self.species)].population if len(self.species) > 1 else 0
            sp.step(prey, pred)

    def report(self) -> dict:
        return {
            "ecology": "agent_ecology",
            "ticks": self.tick_count,
            "species": [s.to_dict() for s in self.species],
            "biodiversity": len([s for s in self.species if s.population > 0]),
        }


def demo():
    eco = Ecology(seed=42)
    eco.add_species("scouts", 30, 0.8, 0.1, 0.05)
    eco.add_species("analysts", 20, 0.6, 0.08, 0.03)
    eco.add_species("builders", 15, 0.7, 0.12, 0.04)
    eco.add_species("sentinels", 10, 0.9, 0.06, 0.07)
    for _ in range(20):
        eco.tick()
    return eco.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
