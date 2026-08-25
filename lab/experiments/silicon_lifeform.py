from __future__ import annotations
"""Silicon Lifeform — emergent digital life simulation.

Digital organisms with genomes, metabolism, reproduction, and evolution.
They compete for silicon resources, mutate, form colonies, and can go
extinct. The simulation tracks evolutionary lineages and fitness landscapes.
"""
import math
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

GENOME_LENGTH = 32
MAX_ENERGY = 100.0
REPRODUCTION_THRESHOLD = 80.0
MUTATION_RATE = 0.05

@dataclass
class Genome:
    genes: List[int] = field(default_factory=list)
    fitness: float = 0.0
    generation: int = 0

    def __post_init__(self):
        if not self.genes:
            self.genes = [0] * GENOME_LENGTH

    def to_hex(self) -> str:
        return "".join(format(g & 0xFF, "02x") for g in self.genes)

    def complexity(self) -> float:
        if not self.genes:
            return 0.0
        unique = len(set(self.genes))
        entropy = -sum(
            (self.genes.count(g) / len(self.genes)) *
            math.log2(self.genes.count(g) / len(self.genes))
            for g in set(self.genes) if self.genes.count(g) > 0
        )
        return entropy + unique / GENOME_LENGTH

@dataclass
class SiliconLifeform:
    organism_id: str
    genome: Genome
    energy: float = 50.0
    age: int = 0
    x: float = 0.0
    y: float = 0.0
    alive: bool = True
    parent_id: Optional[str] = None
    mutations_total: int = 0
    metabolisms_performed: int = 0

    def metabolize(self, resource_quality: float = 1.0) -> float:
        if not self.alive:
            return 0.0
        efficiency = sum(self.genome.genes[:8]) / (8 * 255)
        gain = efficiency * resource_quality * 5.0
        self.energy = min(MAX_ENERGY, self.energy + gain)
        self.metabolisms_performed += 1
        self.energy -= 0.5
        if self.energy <= 0:
            self.alive = False
        return gain

    def can_reproduce(self) -> bool:
        return self.alive and self.energy >= REPRODUCTION_THRESHOLD

    def reproduce(self, rng: random.Random) -> Optional["SiliconLifeform"]:
        if not self.can_reproduce():
            return None
        child_genes = []
        for gene in self.genome.genes:
            if rng.random() < MUTATION_RATE:
                child_genes.append(gene ^ rng.randint(1, 255))
            else:
                child_genes.append(gene)
        child_genome = Genome(
            genes=child_genes,
            generation=self.genome.generation + 1
        )
        self.energy -= 40.0
        child = SiliconLifeform(
            organism_id=f"{self.organism_id}_g{child_genome.generation}_{rng.randint(0,9999):04d}",
            genome=child_genome,
            energy=40.0,
            x=self.x + rng.uniform(-3, 3),
            y=self.y + rng.uniform(-3, 3),
            parent_id=self.organism_id,
            mutations_total=sum(1 for i in range(len(child_genes))
                              if child_genes[i] != self.genome.genes[i]),
        )
        child.genome.fitness = child.genome.complexity()
        return child


class SiliconEcosystem:
    def __init__(self, width: float = 100.0, height: float = 100.0, seed: int = 42):
        self.width = width
        self.height = height
        self.rng = random.Random(seed)
        self.organisms: Dict[str, SiliconLifeform] = {}
        self.extinct: List[str] = []
        self.tick = 0
        self.lineage_log: List[Dict] = []
        self.resource_map: List[List[float]] = [
            [self.rng.uniform(0.3, 1.0) for _ in range(int(width))]
            for _ in range(int(height))
        ]

    def seed_population(self, count: int = 10):
        for i in range(count):
            genes = [self.rng.randint(0, 255) for _ in range(GENOME_LENGTH)]
            organism = SiliconLifeform(
                organism_id=f"organism_{i:04d}",
                genome=Genome(genes=genes),
                energy=self.rng.uniform(30, 70),
                x=self.rng.uniform(0, self.width),
                y=self.rng.uniform(0, self.height),
            )
            organism.genome.fitness = organism.genome.complexity()
            self.organisms[organism.organism_id] = organism

    def _resource_at(self, x: float, y: float) -> float:
        ix = int(max(0, min(x, self.width - 1)))
        iy = int(max(0, min(y, self.height - 1)))
        return self.resource_map[iy][ix]

    def tick_simulation(self) -> Dict:
        self.tick += 1
        births = 0
        deaths = 0

        for org in list(self.organisms.values()):
            if not org.alive:
                self.extinct.append(org.organism_id)
                del self.organisms[org.organism_id]
                deaths += 1
                continue
            org.age += 1
            resource = self._resource_at(org.x, org.y)
            org.metabolize(resource)

        new_borns = []
        for org in list(self.organisms.values()):
            if org.can_reproduce():
                child = org.reproduce(self.rng)
                if child:
                    new_borns.append(child)
                    births += 1

        for child in new_borns:
            self.organisms[child.organism_id] = child
            self.lineage_log.append({
                "tick": self.tick,
                "parent": child.parent_id,
                "child": child.organism_id,
                "mutations": child.mutations_total,
            })

        alive = [o for o in self.organisms.values() if o.alive]
        fitnesses = [o.genome.fitness for o in alive]
        return {
            "tick": self.tick,
            "alive": len(alive),
            "deaths": deaths,
            "births": births,
            "avg_fitness": sum(fitnesses) / max(len(fitnesses), 1),
            "avg_energy": sum(o.energy for o in alive) / max(len(alive), 1),
            "avg_age": sum(o.age for o in alive) / max(len(alive), 1),
            "extinct_total": len(self.extinct),
        }

    def run(self, ticks: int) -> List[Dict]:
        history = []
        for _ in range(ticks):
            history.append(self.tick_simulation())
        return history

    def fitness_landscape(self) -> List[Dict]:
        alive = [o for o in self.organisms.values() if o.alive]
        return sorted(
            [{"id": o.organism_id, "fitness": round(o.genome.fitness, 4),
              "energy": round(o.energy, 1), "age": o.age,
              "generation": o.genome.generation,
              "genome_hex": o.genome.to_hex()[:16] + "..."}
             for o in alive],
            key=lambda x: x["fitness"], reverse=True
        )


def demo():
    ecosystem = SiliconEcosystem(width=50, height=50, seed=42)
    print("=== Silicon Lifeform Simulator ===")
    ecosystem.seed_population(count=15)
    print(f"Seeded {len(ecosystem.organisms)} organisms")

    history = ecosystem.run(ticks=15)
    last = history[-1]
    print(f"\nAfter {last['tick']} ticks:")
    print(f"  Alive: {last['alive']}, Births: {last['births']}, Deaths: {last['deaths']}")
    print(f"  Avg fitness: {last['avg_fitness']:.4f}")
    print(f"  Avg energy: {last['avg_energy']:.1f}")
    print(f"  Extinct total: {last['extinct_total']}")

    print("\nFittest organisms:")
    for org in ecosystem.fitness_landscape()[:5]:
        print(f"  {org['id']}: fitness={org['fitness']}, "
              f"gen={org['generation']}, age={org['age']}")

    print(f"\nLineage events: {len(ecosystem.lineage_log)}")

    return {"history": history, "fitness_landscape": ecosystem.fitness_landscape()}


if __name__ == "__main__":
    demo()
