"""Entropy Gardener — cultivates productive disorder in the system.

Not all entropy is bad. The gardener selectively prunes chaos into
creative disorder — removing harmful randomness while preserving the
useful kind. The gardener knows when to let weeds grow and when to
pull them, maintaining the optimal edge between order and chaos.
"""
from __future__ import annotations

import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ENTROPY_TYPES = {
    "creative_chaos": {"benefit": 0.8, "harm": 0.1, "natural_rate": 0.05},
    "destructive_noise": {"benefit": 0.0, "harm": 0.9, "natural_rate": 0.08},
    "exploratory_spread": {"benefit": 0.6, "harm": 0.2, "natural_rate": 0.03},
    "systemic_drift": {"benefit": 0.3, "harm": 0.5, "natural_rate": 0.04},
    "serendipity_seeds": {"benefit": 0.9, "harm": 0.05, "natural_rate": 0.02},
    "resource_decay": {"benefit": 0.1, "harm": 0.7, "natural_rate": 0.06},
}


class EntropyPlant:
    def __init__(self, entropy_type: str, zone: str = "default"):
        self.entropy_type = entropy_type
        self.zone = zone
        self.specs = ENTROPY_TYPES.get(entropy_type, ENTROPY_TYPES["creative_chaos"])
        self.health = 1.0
        self.growth = 0.0
        self.age = 0
        self.pruned = False

    def grow(self) -> Dict[str, Any]:
        if self.pruned:
            return {"status": "pruned"}
        self.age += 1
        self.growth += self.specs["natural_rate"]
        self.health *= random.uniform(0.95, 1.05)
        self.health = max(0, min(2.0, self.health))
        return {
            "type": self.entropy_type,
            "growth": round(self.growth, 4),
            "health": round(self.health, 3),
            "net_value": round(self.specs["benefit"] - self.specs["harm"], 3),
        }

    def prune(self) -> Dict[str, Any]:
        self.pruned = True
        return {"pruned": self.entropy_type, "zone": self.zone}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.entropy_type,
            "zone": self.zone,
            "growth": round(self.growth, 4),
            "health": round(self.health, 3),
            "age": self.age,
            "pruned": self.pruned,
            "net_value": round(self.specs["benefit"] - self.specs["harm"], 3),
        }


class EntropyGardener:
    def __init__(self):
        self.plants: List[EntropyPlant] = []
        self.harvest_log: List[Dict[str, Any]] = []
        self.prune_log: List[Dict[str, Any]] = []

    def seed(self, entropy_type: str, zone: str = "default") -> Dict[str, Any]:
        plant = EntropyPlant(entropy_type, zone)
        self.plants.append(plant)
        return {"seeded": plant.to_dict()}

    def tend_garden(self) -> List[Dict[str, Any]]:
        results = []
        for plant in self.plants:
            result = plant.grow()
            results.append(result)
        return results

    def selective_prune(self, max_harm: float = 0.5) -> List[Dict[str, Any]]:
        pruned = []
        for plant in self.plants:
            if not plant.pruned and plant.specs["harm"] > max_harm:
                result = plant.prune()
                self.prune_log.append({**result, "time": time.time()})
                pruned.append(result)
        return pruned

    def harvest_benefits(self) -> Dict[str, Any]:
        total_benefit = sum(p.specs["benefit"] * p.growth for p in self.plants if not p.pruned)
        total_harm = sum(p.specs["harm"] * p.growth for p in self.plants if not p.pruned)
        self.harvest_log.append({
            "benefit": round(total_benefit, 4),
            "harm": round(total_harm, 4),
            "net": round(total_benefit - total_harm, 4),
            "time": time.time(),
        })
        return {
            "total_benefit": round(total_benefit, 4),
            "total_harm": round(total_harm, 4),
            "net_value": round(total_benefit - total_harm, 4),
        }

    def garden_stats(self) -> Dict[str, Any]:
        active = [p for p in self.plants if not p.pruned]
        pruned = [p for p in self.plants if p.pruned]
        type_counts: Dict[str, int] = {}
        for p in active:
            type_counts[p.entropy_type] = type_counts.get(p.entropy_type, 0) + 1
        return {
            "total_plants": len(self.plants),
            "active": len(active),
            "pruned": len(pruned),
            "type_distribution": type_counts,
            "total_harvests": len(self.harvest_log),
        }


_gardener = EntropyGardener()


def entropy_gardener_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "seed":
        return _gardener.seed(
            payload.get("entropy_type", "creative_chaos"),
            payload.get("zone", "default"),
        )
    elif action == "tend":
        return {"garden": _gardener.tend_garden()}
    elif action == "prune":
        return {"pruned": _gardener.selective_prune(payload.get("max_harm", 0.5))}
    elif action == "harvest":
        return _gardener.harvest_benefits()
    return {"status": "active", **_gardener.garden_stats()}


handler = entropy_gardener_handler
