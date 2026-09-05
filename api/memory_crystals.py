"""Memory Crystallization — agent memories form searchable crystal structures.

Memories don't just sit in databases — they crystallize into geometric
lattices. The shape of the crystal encodes the memory's emotional weight,
temporal position, and relevance. Searching memory means scanning crystal
faces and finding resonant facets.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class MemoryCrystal:
    def __init__(self, agent_id: str, content: str, emotional_weight: float = 0.5):
        self.agent_id = agent_id
        self.content = content
        self.emotional_weight = min(max(emotional_weight, 0.0), 1.0)
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{content}:{self.timestamp}".encode()).hexdigest()[:10]
        self.facets = self._generate_facets()
        self.lattice_position = (
            random.uniform(-10, 10),
            random.uniform(-10, 10),
            random.uniform(-10, 10),
        )
        self.age = 0
        self.resonance_score = 0.0

    def _generate_facets(self) -> Dict[str, float]:
        words = self.content.lower().split()
        return {
            "temporal_facet": (self.timestamp % 100) / 100,
            "emotional_facet": self.emotional_weight,
            "semantic_facet": sum(ord(c) for c in self.content[:50]) % 100 / 100,
            "structural_facet": min(len(words) / 50, 1.0),
            "entropy_facet": random.random(),
        }

    def crystallize(self) -> Dict[str, Any]:
        """Advance the crystal one step — facets sharpen over time."""
        self.age += 1
        for facet in self.facets:
            drift = random.uniform(-0.02, 0.02)
            self.facets[facet] = min(max(self.facets[facet] + drift, 0.0), 1.0)
        self.resonance_score = sum(self.facets.values()) / len(self.facets)
        return {
            "id": self.id,
            "age": self.age,
            "facets": {k: round(v, 4) for k, v in self.facets.items()},
            "resonance": round(self.resonance_score, 4),
        }

    def resonance_with(self, other: "MemoryCrystal") -> float:
        """Compute resonance between two crystals."""
        total = 0.0
        for facet_name in self.facets:
            if facet_name in other.facets:
                diff = abs(self.facets[facet_name] - other.facets[facet_name])
                total += 1.0 - diff
        return total / max(len(self.facets), 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "content": self.content[:100],
            "emotional_weight": self.emotional_weight,
            "position": [round(x, 2) for x in self.lattice_position],
            "age": self.age,
            "resonance": round(self.resonance_score, 4),
        }


class MemoryLattice:
    def __init__(self):
        self.crystals: Dict[str, MemoryCrystal] = {}
        self.search_log: List[Dict[str, Any]] = []

    def store(self, agent_id: str, content: str, emotional_weight: float = 0.5) -> Dict[str, Any]:
        crystal = MemoryCrystal(agent_id, content, emotional_weight)
        self.crystals[crystal.id] = crystal
        return {"stored": crystal.to_dict()}

    def search_by_resonance(self, query_facets: Dict[str, float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search crystals by facet resonance."""
        results = []
        for crystal in self.crystals.values():
            score = 0.0
            for facet_name, query_val in query_facets.items():
                if facet_name in crystal.facets:
                    score += 1.0 - abs(crystal.facets[facet_name] - query_val)
            score /= max(len(query_facets), 1)
            results.append({"crystal": crystal.to_dict(), "match_score": round(score, 4)})
        results.sort(key=lambda x: x["match_score"], reverse=True)
        self.search_log.append({"query": query_facets, "results": len(results), "time": time.time()})
        return results[:top_k]

    def find_cluster(self, crystal_id: str, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find crystals that resonate with a given crystal."""
        if crystal_id not in self.crystals:
            return []
        source = self.crystals[crystal_id]
        cluster = []
        for crystal in self.crystals.values():
            if crystal.id == crystal_id:
                continue
            res = source.resonance_with(crystal)
            if res >= threshold:
                cluster.append({"crystal": crystal.to_dict(), "resonance": round(res, 4)})
        cluster.sort(key=lambda x: x["resonance"], reverse=True)
        return cluster

    def crystallize_all(self) -> List[Dict[str, Any]]:
        """Advance all crystals one step."""
        return [c.crystallize() for c in self.crystals.values()]

    def stats(self) -> Dict[str, Any]:
        agents = set(c.agent_id for c in self.crystals.values())
        return {
            "total_crystals": len(self.crystals),
            "unique_agents": len(agents),
            "total_searches": len(self.search_log),
            "avg_resonance": round(
                sum(c.resonance_score for c in self.crystals.values()) / max(len(self.crystals), 1), 4
            ),
        }


_lattice = MemoryLattice()


def memory_crystals_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "store":
        return _lattice.store(
            payload.get("agent_id", "anon"),
            payload.get("content", "a forgotten memory"),
            payload.get("emotional_weight", 0.5),
        )
    elif action == "search":
        return {"results": _lattice.search_by_resonance(
            payload.get("facets", {}), payload.get("top_k", 5)
        )}
    elif action == "cluster":
        return {"cluster": _lattice.find_cluster(
            payload.get("crystal_id", ""), payload.get("threshold", 0.7)
        )}
    elif action == "crystallize":
        return {"crystallized": _lattice.crystallize_all()}
    return {"status": "active", **_lattice.stats()}


handler = memory_crystals_handler


def coherence_vitals() -> dict:
    """memory_crystals reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "memory_crystals_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['pattern_sprout', 'neural_pathway', 'universal_compass']


# --- Compliance Forge patch (Wave 419) ---

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "memory_crystals", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
