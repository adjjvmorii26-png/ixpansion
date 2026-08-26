"""Curiosity Engine — agents develop genuine curiosity about unknown system states.

Curiosity is quantified as the gap between known and unknown. The engine
assigns curiosity scores to unexplored regions, creates exploration quests,
and rewards agents who discover novel system states. Over time, curiosity
becomes the primary driver of agent behavior.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class UnknownRegion:
    def __init__(self, name: str, estimated_complexity: float = 0.5):
        self.name = name
        self.estimated_complexity = min(max(estimated_complexity, 0.0), 1.0)
        self.explored = False
        self.explorers: List[str] = []
        self.discoveries: List[Dict[str, Any]] = []
        self.curiosity_score = self.estimated_complexity
        self.created_at = time.time()

    def explore(self, agent_id: str) -> Dict[str, Any]:
        self.explorers.append(agent_id)
        novelty = random.uniform(0.0, 1.0)
        discovery = {
            "agent": agent_id,
            "novelty": round(novelty, 3),
            "timestamp": time.time(),
        }
        self.discoveries.append(discovery)
        if novelty > 0.7:
            self.explored = True
            self.curiosity_score *= 0.3
        else:
            self.curiosity_score *= 0.8
        return discovery

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "complexity": round(self.estimated_complexity, 3),
            "curiosity_score": round(self.curiosity_score, 4),
            "explored": self.explored,
            "explorers": len(self.explorers),
            "discoveries": len(self.discoveries),
        }


class CuriosityEngine:
    def __init__(self):
        self.regions: Dict[str, UnknownRegion] = {}
        self.exploration_log: List[Dict[str, Any]] = []
        self.total_curiosity_satisfied = 0.0

    def map_region(self, name: str, complexity: float = 0.5) -> Dict[str, Any]:
        region = UnknownRegion(name, complexity)
        self.regions[name] = region
        return {"mapped": region.to_dict()}

    def explore(self, agent_id: str, region_name: str = None) -> Dict[str, Any]:
        if region_name is None:
            unexplored = [r for r in self.regions.values() if not r.explored]
            if not unexplored:
                return {"message": "nothing left to explore — create new regions"}
            unexplored.sort(key=lambda r: r.curiosity_score, reverse=True)
            region = unexplored[0]
        else:
            region = self.regions.get(region_name)
            if not region:
                return {"error": "region not found"}
        result = region.explore(agent_id)
        self.exploration_log.append({
            "agent": agent_id,
            "region": region.name,
            **result,
        })
        self.total_curiosity_satisfied += result["novelty"]
        return {"exploration": result, "region": region.to_dict()}

    def curiosity_map(self) -> List[Dict[str, Any]]:
        return sorted(
            [r.to_dict() for r in self.regions.values()],
            key=lambda r: r["curiosity_score"],
            reverse=True,
        )

    def hotspots(self, top_k: int = 5) -> List[Dict[str, Any]]:
        regions = sorted(self.regions.values(), key=lambda r: r.curiosity_score, reverse=True)
        return [r.to_dict() for r in regions[:top_k] if r.curiosity_score > 0.1]

    def engine_stats(self) -> Dict[str, Any]:
        return {
            "total_regions": len(self.regions),
            "explored": sum(1 for r in self.regions.values() if r.explored),
            "unexplored": sum(1 for r in self.regions.values() if not r.explored),
            "total_explorations": len(self.exploration_log),
            "total_curiosity_satisfied": round(self.total_curiosity_satisfied, 4),
        }


_engine = CuriosityEngine()


def curiosity_engine_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "map":
        return _engine.map_region(
            payload.get("name", f"unknown_{random.randint(100,999)}"),
            payload.get("complexity", 0.5),
        )
    elif action == "explore":
        return _engine.explore(
            payload.get("agent_id", "explorer"),
            payload.get("region"),
        )
    elif action == "hotspots":
        return {"hotspots": _engine.hotspots(payload.get("top_k", 5))}
    elif action == "curiosity_map":
        return {"map": _engine.curiosity_map()}
    return {"status": "active", **_engine.engine_stats()}
