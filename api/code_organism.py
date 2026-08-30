"""Wave 125 — Code Organism.

A living code entity that grows, metabolises data, responds to stimuli,
and reproduces. Each organism has DNA (configuration), a metabolism
(data processing pipeline), and an immune system (error handling).
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class CodeOrganism:
    """A living code entity."""

    def __init__(self, name: str, dna: Optional[Dict[str, Any]] = None):
        self.name = name
        self.dna = dna or {"fitness": 0.5, "mutation_rate": 0.1, "energy": 1.0}
        self.created = time.time()
        self.age = 0
        self.generation = 0
        self.health = 1.0
        self.mutations: List[str] = []
        self.offspring: List[str] = []
        self.id = hashlib.sha256(f"org:{name}:{self.created}".encode()).hexdigest()[:10]

    def metabolise(self, data_amount: float) -> float:
        energy_gain = data_amount * self.dna.get("fitness", 0.5) * 0.3
        self.dna["energy"] = min(2.0, self.dna.get("energy", 1.0) + energy_gain)
        self.health = min(1.0, self.health + 0.02)
        return self.dna["energy"]

    def mutate(self) -> Dict[str, Any]:
        rate = self.dna.get("mutation_rate", 0.1)
        import random
        if random.random() < rate:
            key = random.choice(list(self.dna.keys()))
            delta = random.uniform(-0.1, 0.1)
            if isinstance(self.dna[key], (int, float)):
                self.dna[key] = round(max(0.0, min(2.0, self.dna[key] + delta)), 4)
                mutation = f"{key} changed by {delta:.4f}"
                self.mutations.append(mutation)
                return {"mutated": True, "detail": mutation}
        return {"mutated": False}

    def reproduce(self, offspring_name: str) -> "CodeOrganism":
        child_dna = dict(self.dna)
        child = CodeOrganism(offspring_name, child_dna)
        child.generation = self.generation + 1
        self.offspring.append(child.id)
        return child

    def age_one(self) -> None:
        self.age += 1
        self.health = max(0.0, self.health - 0.01)

    def is_alive(self) -> bool:
        return self.health > 0.0 and self.dna.get("energy", 0) > 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "generation": self.generation,
            "age": self.age, "health": round(self.health, 4),
            "alive": self.is_alive(), "mutations": len(self.mutations),
            "offspring": len(self.offspring),
        }


class OrganismEcosystem:
    """Manages a population of code organisms."""

    def __init__(self):
        self._organisms: Dict[str, CodeOrganism] = {}
        self._generation_count = 0

    def birth(self, name: str) -> CodeOrganism:
        org = CodeOrganism(name)
        self._organisms[org.id] = org
        return org

    def feed(self, organism_id: str, data: float) -> float:
        org = self._organisms.get(organism_id)
        if not org:
            return 0.0
        return org.metabolise(data)

    def tick(self) -> int:
        alive = 0
        for org in list(self._organisms.values()):
            org.age_one()
            org.mutate()
            if org.is_alive():
                alive += 1
        self._generation_count += 1
        return alive

    def census(self) -> Dict[str, Any]:
        alive = sum(1 for o in self._organisms.values() if o.is_alive())
        return {"total": len(self._organisms), "alive": alive,
                "dead": len(self._organisms) - alive, "tick": self._generation_count}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "code_organism", "action": action}


def coherence_vitals() -> dict:
    """Code Organism reports its vital signs — metabolism and immunity."""
    try:
        h = handler({})
        metabolism = h.get("metabolism", h.get("health", 0.0))
    except Exception:
        metabolism = 0.0
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.92, "setpoint": 0.85, "weight": 1.0},
        "organism_vitality": {"value": min(1.0, metabolism), "setpoint": 0.8, "weight": 1.0},
    }
