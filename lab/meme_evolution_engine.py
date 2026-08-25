"""Meme Evolution Engine — Memes that evolve, compete, and reproduce.

Each meme is a unit of cultural information that replicates, mutates,
and competes for attention. The fittest memes survive and spread through
the codebase's "culture."
"""
from __future__ import annotations
import hashlib
import random
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class Meme:
    def __init__(self, meme_id: str, content: str, fitness: float, generation: int = 0):
        self.id = meme_id
        self.content = content
        self.fitness = fitness
        self.generation = generation
        self.reproduction_count = 0
        self.offspring: list[str] = []
        self.born = time.time()

    def mutate(self, rng: random.Random, rate: float = 0.1) -> str:
        chars = list(self.content)
        for i in range(len(chars)):
            if rng.random() < rate:
                chars[i] = rng.choice("abcdefghijklmnopqrstuvwxyz_*#@!")
        return "".join(chars)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "content": self.content,
            "fitness": round(self.fitness, 4),
            "generation": self.generation,
            "offspring": len(self.offspring),
        }


class MemePopulation:
    def __init__(self, seed=42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.mememes: dict[str, Meme] = {}
        self.generation = 0
        self.history: list[dict] = []

    def seed_memes(self, count: int = 20):
        seeds = [
            "fractal_growth", "quantum_entanglement", "entropy_reversal",
            "agent_communion", "realm_fusion", "signal_propagation",
            "neural_plasticity", "temporal_recursion", "paradox_synthesis",
            "consciousness_emergence", "gravitational_coding", "morphic_resonance",
            "mycelial_network", "dream_archaeology", "cosmic_fabric",
            "nebula_compiler", "photon_logic", "vortex_topology",
            "prism_refraction", "meridian_routing",
        ]
        for i in range(min(count, len(seeds))):
            meme = Meme(f"meme_{i}", seeds[i], self.rng.uniform(0.3, 0.9))
            self.mememes[meme.id] = meme

    def evolve_step(self):
        self.generation += 1
        # Selection: remove weakest 20%
        sorted_memes = sorted(self.mememes.values(), key=lambda m: m.fitness, reverse=True)
        survivors = sorted_memes[:max(5, int(len(sorted_memes) * 0.6))]

        # Reproduction: top 30% each produce 1 offspring
        parents = survivors[:max(1, int(len(survivors) * 0.3))]
        new_memes = []
        for parent in parents:
            child_content = parent.mutate(self.rng, rate=0.15)
            child_fitness = max(0.1, parent.fitness + self.rng.uniform(-0.15, 0.15))
            child = Meme(f"meme_{len(self.mememes) + len(new_memes)}",
                        child_content, child_fitness, self.generation)
            parent.offspring.append(child.id)
            parent.reproduction_count += 1
            new_memes.append(child)

        # Genetic drift: random fitness changes
        for meme in survivors:
            meme.fitness = max(0.1, min(1.0, meme.fitness + self.rng.uniform(-0.05, 0.05)))

        self.mememes = {m.id: m for m in survivors}
        for m in new_memes:
            self.mememes[m.id] = m

        self.history.append({
            "generation": self.generation,
            "population": len(self.mememes),
            "avg_fitness": round(sum(m.fitness for m in self.mememes.values()) / max(1, len(self.mememes)), 4),
            "best_fitness": round(max(m.fitness for m in self.mememes.values()), 4) if self.mememes else 0,
        })

    def simulate(self, generations: int = 20) -> dict:
        for _ in range(generations):
            self.evolve_step()
        best = max(self.mememes.values(), key=lambda m: m.fitness) if self.mememes else None
        return {
            "generations": generations,
            "final_population": len(self.mememes),
            "best_meme": best.to_dict() if best else None,
            "history": self.history[-5:],
        }

    def report(self) -> dict:
        return {
            "engine": "meme_evolution_engine",
            "generation": self.generation,
            "population": len(self.mememes),
            "avg_fitness": round(
                sum(m.fitness for m in self.mememes.values()) / max(1, len(self.mememes)), 4
            ),
            "top_memes": [m.to_dict() for m in sorted(
                self.mememes.values(), key=lambda m: m.fitness, reverse=True
            )[:5]],
        }


def demo():
    engine = MemePopulation(seed=42)
    engine.seed_memes(20)
    sim = engine.simulate(generations=25)
    return {"simulation": sim, "report": engine.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
