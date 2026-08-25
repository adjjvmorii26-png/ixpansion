"""Speciation Engine — agents evolve and speciate based on usage patterns.

New agent species emerge from combinations of existing ones. Users can
buy "evolution seeds" to guide speciation toward desired capabilities.
Each species has unique traits, strengths, and weaknesses.

Usage:
    POST /api/speciation/evolve     — evolve a new species
    GET  /api/speciation/catalog    — view all species
    POST /api/speciation/breed      — cross-breed two species
    POST /api/speciation/buy_seed   — buy an evolution seed
    GET  /api/speciation/phylogeny  — view evolutionary tree
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

BASE_TRAITS = [
    "speed", "endurance", "perception", "creativity",
    "precision", "adaptability", "empathy", "aggression",
]

SPECIES_COUNTER = 0


def _mutate_traits(parent_traits: Dict[str, float], mutation_rate: float = 0.2) -> Dict[str, float]:
    """Mutate traits with small random perturbations."""
    new_traits = {}
    for trait, value in parent_traits.items():
        delta = random.gauss(0, mutation_rate)
        new_traits[trait] = round(max(0.0, min(1.0, value + delta)), 3)
    return new_traits


def _species_name(traits: Dict[str, float]) -> str:
    """Generate a name from dominant traits."""
    dominant = sorted(traits.items(), key=lambda x: x[1], reverse=True)[:2]
    prefixes = {"speed": "Swift", "endurance": "Iron", "perception": "Keen",
                "creativity": "Dream", "precision": "Sharp", "adaptability": "Fluid",
                "empathy": "Sage", "aggression": "Fierce"}
    suffixes = ["ling", "born", "weaver", "drift", "shade", "spark", "root", "wave"]
    return f"{prefixes.get(dominant[0][0], 'Null')}{random.choice(suffixes)}"


class SpeciationEngine:
    def __init__(self):
        global SPECIES_COUNTER
        self.species: Dict[str, Dict] = {}
        self.phylogeny: List[Dict] = []
        self.seeds_sold = 0
        self._load()
        SPECIES_COUNTER = len(self.species)

    def _load(self):
        path = ROOT / ".runtime" / "speciation.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.species = data.get("species", {})
            self.phylogeny = data.get("phylogeny", [])
            self.seeds_sold = data.get("seeds_sold", 0)

    def _save(self):
        path = ROOT / ".runtime" / "speciation.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "species": self.species,
            "phylogeny": self.phylogeny[-500:],
            "seeds_sold": self.seeds_sold,
        }, indent=2))

    def evolve(self, origin: str = "primordial") -> Dict:
        global SPECIES_COUNTER
        SPECIES_COUNTER += 1
        sid = f"sp_{SPECIES_COUNTER:04d}"
        traits = {t: round(random.uniform(0.1, 0.9), 3) for t in BASE_TRAITS}
        dominant = max(traits, key=traits.get)
        name = _species_name(traits)
        self.species[sid] = {
            "name": name,
            "origin": origin,
            "traits": traits,
            "dominant_trait": dominant,
            "generation": 1,
            "fitness": round(sum(traits.values()) / len(traits), 4),
            "born": time.time(),
        }
        self.phylogeny.append({
            "event": "speciation", "species_id": sid,
            "name": name, "origin": origin,
            "generation": 1, "timestamp": time.time(),
        })
        self._save()
        return {"species_id": sid, "name": name, "traits": traits, "fitness": self.species[sid]["fitness"]}

    def catalog(self) -> List[Dict]:
        return [{"id": k, **v} for k, v in self.species.items()]

    def breed(self, parent_a: str, parent_b: str) -> Dict:
        if parent_a not in self.species or parent_b not in self.species:
            return {"error": "unknown species"}
        global SPECIES_COUNTER
        SPECIES_COUNTER += 1
        sid = f"sp_{SPECIES_COUNTER:04d}"
        pa = self.species[parent_a]["traits"]
        pb = self.species[parent_b]["traits"]
        child_traits = {}
        for trait in BASE_TRAITS:
            avg = (pa.get(trait, 0.5) + pb.get(trait, 0.5)) / 2
            child_traits[trait] = round(avg, 3)
        child_traits = _mutate_traits(child_traits, 0.15)
        name = _species_name(child_traits)
        gen = max(self.species[parent_a]["generation"], self.species[parent_b]["generation"]) + 1
        self.species[sid] = {
            "name": name,
            "origin": f"breed:{parent_a}+{parent_b}",
            "traits": child_traits,
            "dominant_trait": max(child_traits, key=child_traits.get),
            "generation": gen,
            "fitness": round(sum(child_traits.values()) / len(child_traits), 4),
            "born": time.time(),
        }
        self.phylogeny.append({
            "event": "breeding", "species_id": sid,
            "parents": [parent_a, parent_b], "name": name,
            "generation": gen, "timestamp": time.time(),
        })
        self._save()
        return {"species_id": sid, "name": name, "generation": gen, "fitness": self.species[sid]["fitness"]}

    def buy_seed(self, buyer: str, target_trait: str) -> Dict:
        if target_trait not in BASE_TRAITS:
            return {"error": f"unknown trait: {target_trait}"}
        seed_id = hashlib.sha256(f"{buyer}:{target_trait}:{time.time()}".encode()).hexdigest()[:10]
        self.seeds_sold += 1
        self._save()
        return {
            "seed_id": seed_id, "target_trait": target_trait,
            "buyer": buyer, "boost": 0.2,
            "instructions": f"Apply seed to next evolution to boost {target_trait} by 0.2",
        }

    def phylogeny_tree(self) -> List[Dict]:
        return self.phylogeny


def handler(request, response):
    se = SpeciationEngine()
    return {"species_count": len(se.species), "traits": BASE_TRAITS}


def demo():
    se = SpeciationEngine()
    print("=== Speciation Engine ===")
    sp1 = se.evolve("big_bang")
    sp2 = se.evolve("big_bang")
    print(f"Evolved: {sp1['name']} (fitness={sp1['fitness']})")
    print(f"Evolved: {sp2['name']} (fitness={sp2['fitness']})")

    child = se.breed(sp1["species_id"], sp2["species_id"])
    print(f"\nBred: {child['name']} gen={child['generation']} fitness={child['fitness']}")

    seed = se.buy_seed("user_1", "creativity")
    print(f"\nSeed bought: {seed['seed_id']} → {seed['target_trait']}")

    print(f"\nCatalog: {len(se.catalog())} species")
    print(f"Phylogeny: {len(se.phylogeny_tree())} events")
    return {"species": len(se.species)}


if __name__ == "__main__":
    demo()
