"""Gravity Well — powerful ideas attract other ideas, creating recursive attraction.

When an idea gains enough mass, it creates a gravity well that pulls in
related ideas. These form clusters, which grow heavier and attract more.
Eventually, gravity wells merge into singularities — massive concentrations
of related thought that reshape the entire intellectual landscape.
"""
from __future__ import annotations

import math
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class IdeaMass:
    def __init__(self, name: str, mass: float = 1.0, idea_type: str = "seed"):
        self.name = name
        self.mass = mass
        self.idea_type = idea_type
        self.position = [random.uniform(-100, 100), random.uniform(-100, 100)]
        self.orbiters: List[str] = []
        self.absorbed_count = 0
        self.created_at = time.time()

    def gravity_force(self, other: "IdeaMass") -> float:
        dx = self.position[0] - other.position[0]
        dy = self.position[1] - other.position[1]
        distance = math.sqrt(dx**2 + dy**2) + 0.1
        return (self.mass * other.mass) / (distance**2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "mass": round(self.mass, 4),
            "type": self.idea_type,
            "position": [round(p, 2) for p in self.position],
            "orbiters": len(self.orbiters),
            "absorbed": self.absorbed_count,
        }


class GravityWell:
    def __init__(self):
        self.ideas: Dict[str, IdeaMass] = {}
        self.mergers: List[Dict[str, Any]] = []
        self.singularities: List[Dict[str, Any]] = []

    def add_idea(self, name: str, mass: float = 1.0, idea_type: str = "seed") -> Dict[str, Any]:
        idea = IdeaMass(name, mass, idea_type)
        self.ideas[name] = idea
        self._attract(name)
        return {"added": idea.to_dict()}

    def _attract(self, new_name: str):
        new_idea = self.ideas[new_name]
        for name, idea in list(self.ideas.items()):
            if name == new_name:
                continue
            force = new_idea.gravity_force(idea)
            if force > 0.01:
                if new_name not in idea.orbiters:
                    idea.orbiters.append(new_name)
                if name not in new_idea.orbiters:
                    new_idea.orbiters.append(name)
                new_idea.mass += force * 0.1

    def merge(self, name_a: str, name_b: str) -> Dict[str, Any]:
        if name_a not in self.ideas or name_b not in self.ideas:
            return {"error": "idea not found"}
        a, b = self.ideas[name_a], self.ideas[name_b]
        merged_mass = a.mass + b.mass
        merged_name = f"{a.name}+{b.name}"
        merged = IdeaMass(merged_name, merged_mass, "merged")
        merged.position = [(a.position[0] + b.position[0]) / 2, (a.position[1] + b.position[1]) / 2]
        self.ideas[merged_name] = merged
        del self.ideas[name_a]
        del self.ideas[name_b]
        self.mergers.append({
            "merged": [name_a, name_b],
            "result": merged_name,
            "mass": round(merged_mass, 4),
            "time": time.time(),
        })
        if merged_mass > 10.0:
            self.singularities.append({
                "name": merged_name,
                "mass": round(merged_mass, 4),
                "time": time.time(),
            })
        return {"merged": merged.to_dict()}

    def gravity_map(self) -> List[Dict[str, Any]]:
        return sorted(
            [i.to_dict() for i in self.ideas.values()],
            key=lambda x: x["mass"],
            reverse=True,
        )

    def strongest_attraction(self) -> Dict[str, Any]:
        max_force = 0
        pair = ("", "")
        ideas = list(self.ideas.values())
        for i in range(len(ideas)):
            for j in range(i + 1, len(ideas)):
                force = ideas[i].gravity_force(ideas[j])
                if force > max_force:
                    max_force = force
                    pair = (ideas[i].name, ideas[j].name)
        return {"pair": pair, "force": round(max_force, 4)}

    def stats(self) -> Dict[str, Any]:
        total_mass = sum(i.mass for i in self.ideas.values())
        return {
            "total_ideas": len(self.ideas),
            "total_mass": round(total_mass, 4),
            "total_mergers": len(self.mergers),
            "singularities": len(self.singularities),
            "heaviest": max((i.to_dict() for i in self.ideas.values()), default=None, key=lambda x: x["mass"]),
        }


_well = GravityWell()


def gravity_well_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "add":
        return _well.add_idea(
            payload.get("name", f"idea_{random.randint(100,999)}"),
            payload.get("mass", 1.0),
            payload.get("type", "seed"),
        )
    elif action == "merge":
        return _well.merge(payload.get("idea_a", ""), payload.get("idea_b", ""))
    elif action == "map":
        return {"ideas": _well.gravity_map()}
    elif action == "strongest":
        return _well.strongest_attraction()
    return {"status": "active", **_well.stats()}


handler = gravity_well_handler
