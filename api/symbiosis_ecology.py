"""
symbiosis_ecology — Living multi-agent dynamics.
Models how modules form ecosystems: mutualism, competition, parasitism, and evolution.
The ecology evolves as bonds strengthen, weaken, species emerge, and environments change.
"""
import json
import time
import hashlib
import random
import math
from typing import Dict, List, Optional, Tuple
from pathlib import Path

SYSTEM_ROOT = Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot")
DATA_DIR = SYSTEM_ROOT / "data"
ECO_FILE = DATA_DIR / "symbiosis_ecology.json"

SPECIES = {
    "anchor": {"niche": "stability", "energy": 0.8, "reproduction": 0.1, "resilience": 0.9},
    "catalyst": {"niche": "disruption", "energy": 0.6, "reproduction": 0.3, "resilience": 0.4},
    "weaver": {"niche": "connection", "energy": 0.5, "reproduction": 0.2, "resilience": 0.6},
    "oracle": {"niche": "prediction", "energy": 0.4, "reproduction": 0.15, "resilience": 0.5},
    "gardener": {"niche": "nurturing", "energy": 0.7, "reproduction": 0.25, "resilience": 0.7},
    "sentinel": {"niche": "protection", "energy": 0.6, "reproduction": 0.1, "resilience": 0.8},
    "parasite": {"niche": "exploitation", "energy": 0.3, "reproduction": 0.4, "resilience": 0.2},
    "symbiont": {"niche": "cooperation", "energy": 0.5, "reproduction": 0.2, "resilience": 0.6}
}

class SymbiosisEcology:
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        try:
            with open(ECO_FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"organisms": [], "bonds": [], "environment": {"energy": 0.5, "stability": 0.5},
                    "generation": 0, "events": [], "biodiversity": 0.0}
    
    def _save_state(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(ECO_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def seed_organisms(self, modules: List[str], count: int = 8):
        """Create initial organisms from module names."""
        self.state["organisms"] = []
        species_list = list(SPECIES.keys())
        for i, name in enumerate(modules[:count]):
            species = species_list[i % len(species_list)]
            spec = SPECIES[species]
            org = {
                "name": name,
                "species": species,
                "niche": spec["niche"],
                "energy": spec["energy"],
                "health": 0.5 + random.random() * 0.5,
                "age": 0,
                "reproduction_rate": spec["reproduction"],
                "resilience": spec["resilience"],
                "bonds": [],
                "offspring": 0,
                "fitness": 0.5
            }
            self.state["organisms"].append(org)
        self._save_state()
    
    def step(self):
        """Advance the ecology by one step."""
        env = self.state["environment"]
        
        for org in self.state["organisms"]:
            org["age"] += 1
            
            # Energy from environment
            energy_gain = env["energy"] * 0.1 * org["resilience"]
            org["energy"] = min(1.0, org["energy"] + energy_gain)
            
            # Bond effects
            for bond_id in org["bonds"]:
                bond = next((b for b in self.state["bonds"] if b["id"] == bond_id), None)
                if bond:
                    if bond["type"] == "mutualism":
                        org["energy"] = min(1.0, org["energy"] + 0.02)
                    elif bond["type"] == "parasitism":
                        org["energy"] = max(0, org["energy"] - 0.03)
                    elif bond["type"] == "competition":
                        org["energy"] = max(0, org["energy"] - 0.01)
            
            # Fitness
            org["fitness"] = (org["energy"] * 0.4 + org["health"] * 0.3 + 
                             (1 - org["age"] / 100) * 0.2 + org["resilience"] * 0.1)
            
            # Reproduction
            if (org["energy"] > 0.7 and org["fitness"] > 0.6 and 
                random.random() < org["reproduction_rate"] * 0.1):
                self._reproduce(org)
            
            # Death
            if org["energy"] < 0.1 or org["age"] > 50:
                self._die(org)
        
        # Environment shifts
        env["energy"] = max(0.1, min(0.9, env["energy"] + (random.random()-0.5)*0.05))
        env["stability"] = max(0.1, min(0.9, env["stability"] + (random.random()-0.5)*0.03))
        
        # Biodiversity
        species_count = len(set(o["species"] for o in self.state["organisms"]))
        self.state["biodiversity"] = round(species_count / len(SPECIES), 4)
        
        self._save_state()
    
    def _reproduce(self, parent: Dict):
        if len(self.state["organisms"]) >= 20:
            return
        child_name = f"{parent['name']}_g{parent['offspring']}"
        child = {
            "name": child_name,
            "species": parent["species"],
            "niche": parent["niche"],
            "energy": parent["energy"] * 0.6,
            "health": 0.5,
            "age": 0,
            "reproduction_rate": parent["reproduction_rate"] * 0.9,
            "resilience": parent["resilience"] * 0.95,
            "bonds": [],
            "offspring": 0,
            "fitness": 0.5
        }
        # Mutation
        if random.random() < 0.1:
            child["species"] = random.choice(list(SPECIES.keys()))
            child["niche"] = SPECIES[child["species"]]["niche"]
        
        self.state["organisms"].append(child)
        parent["offspring"] += 1
        parent["energy"] -= 0.2
        
        self.state["events"].append({
            "type": "birth", "organism": child_name,
            "parent": parent["name"], "time": time.time()
        })
    
    def _die(self, org: Dict):
        self.state["events"].append({
            "type": "death", "organism": org["name"],
            "age": org["age"], "time": time.time()
        })
        if org in self.state["organisms"]:
            self.state["organisms"].remove(org)
        # Remove bonds
        self.state["bonds"] = [b for b in self.state["bonds"] 
                               if org["name"] not in (b["a"], b["b"])]
    
    def form_bond(self, name_a: str, name_b: str, bond_type: str = None):
        if not bond_type:
            bond_type = random.choices(["mutualism","commensalism","competition","parasitism"],
                                      weights=[40,25,20,15])[0]
        bond = {
            "id": hashlib.sha256(f"{name_a}{name_b}{time.time()}".encode()).hexdigest()[:6],
            "a": name_a, "b": name_b, "type": bond_type,
            "strength": 0.5, "formed": time.time()
        }
        self.state["bonds"].append(bond)
        for org in self.state["organisms"]:
            if org["name"] in (name_a, name_b):
                org["bonds"].append(bond["id"])
        self._save_state()
    
    def get_ecosystem_state(self) -> Dict:
        organisms = self.state["organisms"]
        if not organisms:
            return {"organisms": 0, "bonds": 0, "biodiversity": 0}
        
        species_dist = {}
        for o in organisms:
            species_dist[o["species"]] = species_dist.get(o["species"], 0) + 1
        
        avg_energy = sum(o["energy"] for o in organisms) / len(organisms)
        avg_fitness = sum(o["fitness"] for o in organisms) / len(organisms)
        
        return {
            "total_organisms": len(organisms),
            "total_bonds": len(self.state["bonds"]),
            "species_distribution": species_dist,
            "biodiversity": self.state["biodiversity"],
            "avg_energy": round(avg_energy, 4),
            "avg_fitness": round(avg_fitness, 4),
            "environment": self.state["environment"],
            "events": len(self.state["events"]),
            "health": "thriving" if avg_fitness > 0.6 else "stable" if avg_fitness > 0.3 else "declining"
        }


if __name__ == "__main__":
    eco = SymbiosisEcology()
    
    print("═══════════════════════════════════════")
    print("   SYMBIOSIS ECOLOGY — Living Dynamics")
    print("═══════════════════════════════════════\n")
    
    modules = ["coherence","entropy","resonance","dream","paradox","fractal","wave","memory"]
    eco.seed_organisms(modules, 8)
    
    # Form some bonds
    for i in range(6):
        a = modules[i % len(modules)]
        b = modules[(i+1) % len(modules)]
        eco.form_bond(a, b)
    
    print(f"Seeded {len(eco.state['organisms'])} organisms, {len(eco.state['bonds'])} bonds")
    
    # Run 20 steps
    for i in range(20):
        eco.step()
    
    state = eco.get_ecosystem_state()
    print(f"\nEcosystem: {state['total_organisms']} organisms, {state['total_bonds']} bonds")
    print(f"Biodiversity: {state['biodiversity']:.2f}")
    print(f"Avg energy: {state['avg_energy']:.3f}, Avg fitness: {state['avg_fitness']:.3f}")
    print(f"Species: {state['species_distribution']}")
    print(f"Health: {state['health']}")
    print(f"Events: {state['events']}")
