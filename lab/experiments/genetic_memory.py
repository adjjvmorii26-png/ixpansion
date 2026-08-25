from __future__ import annotations
"""Genetic Memory — hereditary information storage with evolution.

Stores information in a DNA-like structure where past states influence
future behavior. Memory "genes" are inherited across generations, with
mutation and crossover producing novel combinations. The system evolves
its own memory encoding over time.
"""
import math
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

BASES = ["A", "C", "G", "T"]
CODON_SIZE = 3

@dataclass
class Gene:
    codons: List[str] = field(default_factory=list)
    expression_level: float = 1.0
    generation_born: int = 0
    mutations: int = 0

    def to_string(self) -> str:
        return "".join(self.codons)

    def fitness(self) -> float:
        if not self.codons:
            return 0.0
        unique_codons = len(set(self.codons))
        diversity = unique_codons / max(len(self.codons), 1)
        return diversity * self.expression_level

@dataclass
class Genome:
    genes: List[Gene] = field(default_factory=list)
    generation: int = 0
    fitness: float = 0.0
    ancestral_hash: str = ""

    def sequence(self) -> str:
        return "".join(g.to_string() for g in self.genes)

    def compute_fitness(self) -> float:
        if not self.genes:
            return 0.0
        self.fitness = sum(g.fitness() for g in self.genes) / len(self.genes)
        return self.fitness

@dataclass
class MemoryOrganism:
    organism_id: str
    genome: Genome
    age: int = 0
    memories: List[str] = field(default_factory=list)
    lineage: List[str] = field(default_factory=list)

class GeneticMemoryEngine:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.organisms: Dict[str, MemoryOrganism] = {}
        self.generation = 0
        self.evolution_log: List[Dict] = []

    def _text_to_codons(self, text: str) -> List[str]:
        codons = []
        for i in range(0, len(text), CODON_SIZE):
            chunk = text[i:i + CODON_SIZE]
            codon = ""
            for c in chunk:
                idx = ord(c) % len(BASES)
                codon += BASES[idx]
            while len(codon) < CODON_SIZE:
                codon += self.rng.choice(BASES)
            codons.append(codon[:CODON_SIZE])
        return codons

    def create_organism(self, name: str, text: str) -> MemoryOrganism:
        codons = self._text_to_codons(text)
        gene = Gene(codons=codons, generation_born=self.generation)
        # removed duplicate line
        genome = Genome(genes=[gene], generation=self.generation)
        genome.compute_fitness()
        organism = MemoryOrganism(
            organism_id=name, genome=genome, memories=[text],
            lineage=[f"gen_{self.generation}"],
        )
        self.organisms[name] = organism
        return organism

    def mutate(self, name: str, mutation_rate: float = 0.1) -> Optional[MemoryOrganism]:
        if name not in self.organisms:
            return None
        parent = self.organisms[name]
        child_genes = []
        mutations = 0
        for gene in parent.genome.genes:
            new_codons = []
            for codon in gene.codons:
                if self.rng.random() < mutation_rate:
                    idx = self.rng.randint(0, len(codon) - 1)
                    new_char = self.rng.choice(BASES)
                    new_codons.append(codon[:idx] + new_char + codon[idx+1:])
                    mutations += 1
                else:
                    new_codons.append(codon)
            child_genes.append(Gene(
                codons=new_codons,
                expression_level=gene.expression_level * self.rng.uniform(0.8, 1.2),
                generation_born=self.generation,
                mutations=mutations,
            ))

        child_genome = Genome(genes=child_genes, generation=self.generation)
        child_genome.compute_fitness()
        child_name = f"{name}_mut_{self.generation}"
        child = MemoryOrganism(
            organism_id=child_name, genome=child_genome,
            memories=parent.memories.copy(),
            lineage=parent.lineage + [f"gen_{self.generation}"],
        )
        self.organisms[child_name] = child
        return child

    def crossover(self, name_a: str, name_b: str) -> Optional[MemoryOrganism]:
        if name_a not in self.organisms or name_b not in self.organisms:
            return None
        a, b = self.organisms[name_a], self.organisms[name_b]
        child_genes = []
        genes_a = a.genome.genes
        genes_b = b.genome.genes
        max_genes = max(len(genes_a), len(genes_b))
        for i in range(max_genes):
            source = genes_a[i % len(genes_a)] if i % 2 == 0 else genes_b[i % len(genes_b)]
            child_genes.append(Gene(
                codons=source.codons.copy(),
                expression_level=(a.genome.fitness + b.genome.fitness) / 2,
                generation_born=self.generation,
            ))
        child_genome = Genome(genes=child_genes, generation=self.generation)
        child_genome.compute_fitness()
        child_name = f"{name_a}x{name_b}_g{self.generation}"
        child = MemoryOrganism(
            organism_id=child_name, genome=child_genome,
            memories=a.memories + b.memories,
            lineage=a.lineage + b.lineage,
        )
        self.organisms[child_name] = child
        return child

    def evolve_generation(self):
        self.generation += 1
        names = list(self.organisms.keys())
        if len(names) >= 2:
            a, b = self.rng.sample(names, 2)
            self.crossover(a, b)
        for name in names:
            if self.rng.random() < 0.3:
                self.mutate(name)

        self.evolution_log.append({
            "generation": self.generation,
            "population": len(self.organisms),
            "avg_fitness": sum(o.genome.fitness for o in self.organisms.values()) /
                          max(len(self.organisms), 1),
        })

    def run_evolution(self, generations: int = 10) -> List[Dict]:
        for _ in range(generations):
            self.evolve_generation()
        return self.evolution_log

    def population_report(self) -> Dict:
        organisms = list(self.organisms.values())
        return {
            "population": len(organisms),
            "generation": self.generation,
            "avg_fitness": sum(o.genome.fitness for o in organisms) / max(len(organisms), 1),
            "fittest": sorted(
                [{"id": o.organism_id, "fitness": round(o.genome.fitness, 4),
                  "age": o.age, "gen": o.genome.generation}
                 for o in organisms],
                key=lambda x: x["fitness"], reverse=True
            )[:5],
        }


def demo():
    engine = GeneticMemoryEngine(seed=42)
    print("=== Genetic Memory Engine ===")

    texts = [
        ("alpha_memory", "The engine remembers everything"),
        ("beta_memory", "Patterns repeat across generations"),
        ("gamma_memory", "Mutation creates novelty"),
        ("delta_memory", "Crossover combines wisdom"),
        ("epsilon_memory", "Evolution finds better encodings"),
    ]
    for name, text in texts:
        engine.create_organism(name, text)

    print(f"  Initial population: {len(engine.organisms)}")
    history = engine.run_evolution(generations=15)
    print(f"  After {history[-1]['generation']} generations:")
    print(f"    Population: {history[-1]['population']}")
    print(f"    Avg fitness: {history[-1]['avg_fitness']:.4f}")

    report = engine.population_report()
    print("\nFittest organisms:")
    for org in report["fittest"]:
        print(f"  {org['id']}: fitness={org['fitness']}, gen={org['gen']}")

    return {"history": history, "report": report}


if __name__ == "__main__":
    demo()
