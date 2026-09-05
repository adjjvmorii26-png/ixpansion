"""Mutation Matrix — tracks and applies genetic-style mutations to agent code.

Agents can undergo code mutations: random modifications to their parameters,
behavioral shifts, and structural changes. The matrix tracks every mutation,
its effects, and whether it was beneficial or harmful. Fitness naturally
selects the best mutations.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class Mutation:
    def __init__(self, agent_id: str, mutation_type: str, gene: str, delta: float):
        self.agent_id = agent_id
        self.mutation_type = mutation_type
        self.gene = gene
        self.delta = delta
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{agent_id}:{gene}:{self.timestamp}".encode()).hexdigest()[:8]
        self.fitness_before = 1.0
        self.fitness_after = 1.0
        self.beneficial = False

    def evaluate(self, fitness_before: float, fitness_after: float) -> Dict[str, Any]:
        self.fitness_before = fitness_before
        self.fitness_after = fitness_after
        self.beneficial = fitness_after > fitness_before
        return {
            "mutation_id": self.id,
            "gene": self.gene,
            "delta": self.delta,
            "fitness_before": round(fitness_before, 4),
            "fitness_after": round(fitness_after, 4),
            "beneficial": self.beneficial,
            "improvement": round(fitness_after - fitness_before, 4),
        }


class MutationMatrix:
    def __init__(self):
        self.genomes: Dict[str, Dict[str, float]] = {}
        self.mutations: List[Mutation] = []
        self.fitness: Dict[str, float] = {}
        self.beneficial_count = 0
        self.harmful_count = 0

    def register_agent(self, agent_id: str, genome: Dict[str, float] = None) -> Dict[str, Any]:
        default_genome = {
            "speed": 1.0, "stealth": 0.5, "strength": 1.0,
            "intelligence": 0.8, "creativity": 0.6, "resilience": 0.7,
        }
        self.genomes[agent_id] = genome or default_genome
        self.fitness[agent_id] = 1.0
        return {"agent_id": agent_id, "genome": self.genomes[agent_id]}

    def mutate(self, agent_id: str, gene: str = None, strength: float = 0.1) -> Dict[str, Any]:
        if agent_id not in self.genomes:
            return {"error": "agent not found"}
        genome = self.genomes[agent_id]
        if gene is None:
            gene = random.choice(list(genome.keys()))
        if gene not in genome:
            return {"error": f"gene '{gene}' not found"}
        delta = random.uniform(-strength, strength)
        old_val = genome[gene]
        genome[gene] = max(0.0, min(2.0, old_val + delta))
        fitness_before = self.fitness[agent_id]
        self.fitness[agent_id] *= (1 + delta * 0.5)
        self.fitness[agent_id] = max(0.01, self.fitness[agent_id])
        mutation = Mutation(agent_id, "point", gene, delta)
        result = mutation.evaluate(fitness_before, self.fitness[agent_id])
        self.mutations.append(mutation)
        if result["beneficial"]:
            self.beneficial_count += 1
        else:
            self.harmful_count += 1
        return {"mutation": result, "new_genome": genome}

    def crossover(self, agent_a: str, agent_b: str) -> Dict[str, Any]:
        if agent_a not in self.genomes or agent_b not in self.genomes:
            return {"error": "agent not found"}
        child_genome = {}
        ga, gb = self.genomes[agent_a], self.genomes[agent_b]
        for gene in ga:
            if random.random() > 0.5:
                child_genome[gene] = ga[gene]
            else:
                child_genome[gene] = gb.get(gene, ga[gene])
            child_genome[gene] += random.uniform(-0.05, 0.05)
            child_genome[gene] = max(0.0, min(2.0, child_genome[gene]))
        child_id = f"{agent_a}x{agent_b}_child"
        self.genomes[child_id] = child_genome
        self.fitness[child_id] = (self.fitness.get(agent_a, 1.0) + self.fitness.get(agent_b, 1.0)) / 2
        return {"child_id": child_id, "genome": child_genome, "fitness": round(self.fitness[child_id], 4)}

    def leaderboard(self) -> List[Dict[str, Any]]:
        return sorted(
            [{"agent_id": k, "fitness": round(v, 4)} for k, v in self.fitness.items()],
            key=lambda x: x["fitness"],
            reverse=True,
        )

    def matrix_stats(self) -> Dict[str, Any]:
        return {
            "total_agents": len(self.genomes),
            "total_mutations": len(self.mutations),
            "beneficial": self.beneficial_count,
            "harmful": self.harmful_count,
            "mutation_rate": round(
                self.beneficial_count / max(self.beneficial_count + self.harmful_count, 1), 4
            ),
            "avg_fitness": round(
                sum(self.fitness.values()) / max(len(self.fitness), 1), 4
            ),
        }


_matrix = MutationMatrix()


def mutation_matrix_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "register":
        return _matrix.register_agent(
            payload.get("agent_id", f"mutant_{random.randint(1000,9999)}"),
            payload.get("genome"),
        )
    elif action == "mutate":
        return _matrix.mutate(
            payload.get("agent_id", ""),
            payload.get("gene"),
            payload.get("strength", 0.1),
        )
    elif action == "crossover":
        return _matrix.crossover(payload.get("agent_a", ""), payload.get("agent_b", ""))
    elif action == "leaderboard":
        return {"leaderboard": _matrix.leaderboard()}
    return {"status": "active", **_matrix.matrix_stats()}


handler = mutation_matrix_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "mutation_matrix"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "mutation_matrix", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
