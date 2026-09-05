"""Fractal Growth Engine — grows new modules from seed patterns.

Takes a seed description and recursively generates new module concepts
by applying transformation rules. Each generation can branch into
multiple new ideas.
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

TRANSFORMATIONS = {
    "mirror": lambda s: f"anti_{s}",
    "scale": lambda s: f"meta_{s}",
    "invert": lambda s: f"{s}_inverted",
    "combine": lambda s: f"hybrid_{s}",
    "fracture": lambda s: f"shard_of_{s}",
    "bloom": lambda s: f"{s}_garden",
    "warp": lambda s: f"{s}_warped",
    "echo": lambda s: f"echo_of_{s}",
}

SEEDS = [
    "quantum", "entropy", "dream", "memory", "agent",
    "pattern", "time", "space", "chaos", "order",
]


class FractalGrowth:
    def __init__(self):
        self.organisms: Dict[str, Dict] = {}
        self.generation_count = 0
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "fractal_growth.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.organisms = data.get("organisms", {})
            self.generation_count = data.get("generation_count", 0)

    def _save(self):
        path = ROOT / ".runtime" / "fractal_growth.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "organisms": self.organisms,
            "generation_count": self.generation_count,
        }, indent=2))

    def plant_seed(self, seed: str) -> Dict:
        org_id = hashlib.sha256(f"{seed}:{time.time()}".encode()).hexdigest()[:10]
        self.organisms[org_id] = {
            "name": seed, "generation": 0,
            "children": [], "created": time.time(),
        }
        self._save()
        return {"organism_id": org_id, "name": seed, "generation": 0}

    def grow(self, organism_id: str) -> Dict:
        if organism_id not in self.organisms:
            return {"error": "organism not found"}
        parent = self.organisms[organism_id]
        self.generation_count += 1
        num_children = random.randint(1, 3)
        new_children = []
        for _ in range(num_children):
            transform = random.choice(list(TRANSFORMATIONS.keys()))
            child_name = TRANSFORMATIONS[transform](parent["name"])
            child_id = hashlib.sha256(f"{child_name}:{time.time()}:{random.random()}".encode()).hexdigest()[:10]
            self.organisms[child_id] = {
                "name": child_name, "generation": parent["generation"] + 1,
                "parent": organism_id, "transform": transform,
                "children": [], "created": time.time(),
            }
            parent.setdefault("children", []).append(child_id)
            new_children.append({"id": child_id, "name": child_name, "transform": transform})
        self._save()
        return {"parent": parent["name"], "children": new_children, "generation": self.generation_count}

    def tree(self, organism_id: str, depth: int = 3) -> Dict:
        if organism_id not in self.organisms:
            return {"error": "organism not found"}
        org = self.organisms[organism_id]
        node = {"name": org["name"], "generation": org["generation"]}
        if depth > 0 and org.get("children"):
            node["children"] = [self.tree(cid, depth - 1) for cid in org["children"][:3]]
        return node

    def stats(self) -> Dict:
        return {
            "total_organisms": len(self.organisms),
            "total_generations": self.generation_count,
            "max_depth": max((o["generation"] for o in self.organisms.values()), default=0),
        }


def handler(request, response):
    fg = FractalGrowth()
    return fg.stats()


def demo():
    fg = FractalGrowth()
    print("=== Fractal Growth Engine ===")
    seed = fg.plant_seed("quantum")
    print(f"\nPlanted: {seed['name']}")
    for _ in range(3):
        result = fg.grow(seed["organism_id"])
        for child in result["children"]:
            print(f"  -> {child['name']} ({child['transform']})")
    tree = fg.tree(seed["organism_id"], 2)
    print(f"\nTree: {tree['name']} (gen {tree['generation']})")
    return fg.stats()


if __name__ == "__main__":
    demo()

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "fractal_growth"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
