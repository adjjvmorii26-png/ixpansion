"""Dimensional Fold — creates shortcuts between distant system regions.

Like wormholes in spacetime, dimensional folds create instant connections
between any two points in the system. Agents can traverse vast distances
instantly, but folds consume energy and can destabilize if overloaded.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class Fold:
    def __init__(self, origin: str, destination: str, energy_cost: float = 1.0):
        self.origin = origin
        self.destination = destination
        self.energy_cost = energy_cost
        self.stability = 1.0
        self.traversals = 0
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{origin}:{destination}".encode()).hexdigest()[:8]
        self.active = True

    def traverse(self, agent_id: str) -> Dict[str, Any]:
        if not self.active:
            return {"error": "fold collapsed"}
        self.traversals += 1
        self.stability -= 0.05
        if self.stability <= 0:
            self.active = False
        return {
            "agent": agent_id,
            "origin": self.origin,
            "destination": self.destination,
            "traversals": self.traversals,
            "stability": round(self.stability, 3),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "origin": self.origin,
            "destination": self.destination,
            "energy_cost": self.energy_cost,
            "stability": round(self.stability, 3),
            "active": self.active,
            "traversals": self.traversals,
        }


class DimensionalFold:
    def __init__(self):
        self.folds: Dict[str, Fold] = {}
        self.regions: Dict[str, Dict[str, Any]] = {}
        self.fold_log: List[Dict[str, Any]] = []

    def register_region(self, name: str, coordinates: Dict[str, float] = None) -> Dict[str, Any]:
        self.regions[name] = {
            "coordinates": coordinates or {"x": random.uniform(0, 100), "y": random.uniform(0, 100)},
            "visitors": 0,
        }
        return {"registered": name}

    def create_fold(self, origin: str, destination: str, energy_cost: float = 1.0) -> Dict[str, Any]:
        if origin not in self.regions or destination not in self.regions:
            return {"error": "region not found"}
        fold = Fold(origin, destination, energy_cost)
        self.folds[fold.id] = fold
        return {"created": fold.to_dict()}

    def traverse(self, fold_id: str, agent_id: str) -> Dict[str, Any]:
        if fold_id not in self.folds:
            return {"error": "fold not found"}
        result = self.folds[fold_id].traverse(agent_id)
        if "error" not in result:
            self.regions[destination := self.folds[fold_id].destination]["visitors"] += 1
            self.fold_log.append({**result, "time": time.time()})
        return result

    def fold_map(self) -> List[Dict[str, Any]]:
        return [f.to_dict() for f in self.folds.values()]

    def active_folds(self) -> List[Dict[str, Any]]:
        return [f.to_dict() for f in self.folds.values() if f.active]

    def fold_stats(self) -> Dict[str, Any]:
        active = sum(1 for f in self.folds.values() if f.active)
        return {
            "total_regions": len(self.regions),
            "total_folds": len(self.folds),
            "active_folds": active,
            "collapsed_folds": len(self.folds) - active,
            "total_traversals": sum(f.traversals for f in self.folds.values()),
        }


_dimensional = DimensionalFold()


def dimensional_fold_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "register_region":
        return _dimensional.register_region(
            payload.get("name", f"region_{random.randint(100,999)}"),
            payload.get("coordinates"),
        )
    elif action == "create_fold":
        return _dimensional.create_fold(
            payload.get("origin", ""), payload.get("destination", ""),
            payload.get("energy_cost", 1.0),
        )
    elif action == "traverse":
        return _dimensional.traverse(payload.get("fold_id", ""), payload.get("agent_id", "traveler"))
    elif action == "active":
        return {"folds": _dimensional.active_folds()}
    return {"status": "active", **_dimensional.fold_stats()}


handler = dimensional_fold_handler
