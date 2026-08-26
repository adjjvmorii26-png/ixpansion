"""Evolution Simulator — watches species evolve in real-time.

Simulates natural selection, mutation, and fitness landscapes.
Species compete for resources, adapt to changing environments,
and speciate when populations diverge enough.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TRAITS = ["speed", "strength", "cunning", "endurance", "perception", "charisma"]


class EvolutionSimulator:
    def __init__(self):
        self.species: Dict[str, Dict] = []
        self.environment = {"temperature": 0.5, "resources": 0.7, "predation": 0.3}
        self.generation = 0
        self.history: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "evolution_sim.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.species = data.get("species", [])
            self.generation = data.get("generation", 0)
            self.history = data.get("history", [])

    def _save(self):
        path = ROOT / ".runtime" / "evolution_sim.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "species": self.species, "generation": self.generation,
            "history": self.history[-500:],
        }, indent=2))

    def spawn_species(self, name: str = "", population: int = 10) -> Dict:
        name = name or f"Species_{random.randint(100,999)}"
        traits = {t: round(random.uniform(0.1, 0.9), 3) for t in TRAITS}
        fitness = sum(traits.values()) / len(traits)
        sp = {
            "name": name, "population": population,
            "traits": traits, "fitness": round(fitness, 4),
            "born": self.generation,
        }
        self.species.append(sp)
        self._save()
        return {"name": name, "traits": traits, "fitness": fitness}

    def evolve(self) -> Dict:
        self.generation += 1
        for sp in self.species:
            for trait in sp["traits"]:
                mutation = random.gauss(0, 0.05)
                sp["traits"][trait] = max(0, min(1, sp["traits"][trait] + mutation))
            sp["fitness"] = round(sum(sp["traits"].values()) / len(sp["traits"]), 4)
            env_factor = 1.0 - self.environment["predation"] * 0.3
            sp["population"] = max(1, int(sp["population"] * (0.9 + sp["fitness"] * 0.2) * env_factor))
        self.species.sort(key=lambda s: s["fitness"], reverse=True)
        if len(self.species) >= 2:
            top = self.species[0]
            if random.random() < 0.1:
                child_traits = {t: (top["traits"][t] + random.gauss(0, 0.1)) for t in TRAITS}
                child_traits = {t: max(0, min(1, v)) for t, v in child_traits.items()}
                child_name = f"Descendant_{random.randint(100,999)}"
                self.species.append({
                    "name": child_name, "population": 5,
                    "traits": {t: round(v, 3) for t, v in child_traits.items()},
                    "fitness": round(sum(child_traits.values()) / len(child_traits), 4),
                    "born": self.generation,
                })
        entry = {"generation": self.generation, "species_count": len(self.species),
                 "top_fitness": self.species[0]["fitness"] if self.species else 0}
        self.history.append(entry)
        self._save()
        return entry

    def landscape(self) -> List[Dict]:
        return [{"name": s["name"], "fitness": s["fitness"], "population": s["population"]} for s in self.species]


def handler(request, response):
    es = EvolutionSimulator()
    return {"generation": es.generation, "species": len(es.species)}


def demo():
    es = EvolutionSimulator()
    print("=== Evolution Simulator ===")
    es.spawn_species("Alpha")
    es.spawn_species("Beta")
    for _ in range(5):
        result = es.evolve()
        print(f"  Gen {result['generation']}: {result['species_count']} species, top fitness={result['top_fitness']}")
    for sp in es.landscape():
        print(f"    {sp['name']}: fitness={sp['fitness']}, pop={sp['population']}")
    return handler({}, {})


if __name__ == "__main__":
    demo()
