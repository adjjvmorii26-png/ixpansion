"""Quantum Garden — where possibilities grow like plants before collapsing into reality.

Each planted possibility grows through stages: seed, sprout, bloom,
and finally collapse into either reality or void. The garden is a
visual metaphor for how potential becomes actual, with each plant
representing an idea competing for reality.
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

GROWTH_STAGES = ["seed", "sprout", "sapling", "bloom", "collapse"]


class PossibilityPlant:
    def __init__(self, name: str, idea: str, gardener: str):
        self.name = name
        self.idea = idea
        self.gardener = gardener
        self.stage_idx = 0
        self.vitality = 0.5
        self.watered = 0
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{name}:{self.created_at}".encode()).hexdigest()[:8]
        self.collapsed = False
        self.became_reality = False

    @property
    def stage(self) -> str:
        return GROWTH_STAGES[min(self.stage_idx, len(GROWTH_STAGES) - 1)]

    def water(self) -> Dict[str, Any]:
        self.watered += 1
        self.vitality = min(1.0, self.vitality + 0.1)
        return {"plant": self.name, "vitality": round(self.vitality, 3), "stage": self.stage}

    def grow(self) -> Dict[str, Any]:
        if self.collapsed:
            return {"status": "already collapsed"}
        self.vitality *= random.uniform(0.8, 1.1)
        self.vitality = min(max(self.vitality, 0.0), 1.0)
        if self.stage_idx < len(GROWTH_STAGES) - 1:
            self.stage_idx += 1
        if self.stage == "collapse":
            self.collapsed = True
            self.became_reality = self.vitality > 0.5
        return {
            "plant": self.name,
            "stage": self.stage,
            "vitality": round(self.vitality, 3),
            "collapsed": self.collapsed,
            "reality": self.became_reality if self.collapsed else None,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "idea": self.idea[:60],
            "stage": self.stage,
            "vitality": round(self.vitality, 3),
            "watered": self.watered,
            "collapsed": self.collapsed,
        }


class QuantumGarden:
    def __init__(self):
        self.plants: Dict[str, PossibilityPlant] = []
        self.reality_count = 0
        self.void_count = 0

    def plant(self, name: str, idea: str, gardener: str = "gardener") -> Dict[str, Any]:
        p = PossibilityPlant(name, idea, gardener)
        self.plants.append(p)
        return {"planted": p.to_dict()}

    def water(self, plant_id: str) -> Dict[str, Any]:
        for p in self.plants:
            if p.id == plant_id:
                return p.water()
        return {"error": "plant not found"}

    def tend(self) -> List[Dict[str, Any]]:
        results = []
        for p in self.plants:
            if not p.collapsed:
                result = p.grow()
                results.append(result)
                if p.collapsed:
                    if p.became_reality:
                        self.reality_count += 1
                    else:
                        self.void_count += 1
        return results

    def blooming(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.plants if not p.collapsed and p.stage == "bloom"]

    def garden_stats(self) -> Dict[str, Any]:
        alive = sum(1 for p in self.plants if not p.collapsed)
        return {
            "total_plants": len(self.plants),
            "alive": alive,
            "became_reality": self.reality_count,
            "returned_to_void": self.void_count,
        }


_garden = QuantumGarden()


def quantum_garden_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "plant":
        return _garden.plant(
            payload.get("name", f"seed_{random.randint(100,999)}"),
            payload.get("idea", "an possibility"),
            payload.get("gardener", "gardener"),
        )
    elif action == "water":
        return _garden.water(payload.get("plant_id", ""))
    elif action == "tend":
        return {"garden": _garden.tend()}
    elif action == "blooming":
        return {"plants": _garden.blooming()}
    return {"status": "active", **_garden.garden_stats()}


handler = quantum_garden_handler
