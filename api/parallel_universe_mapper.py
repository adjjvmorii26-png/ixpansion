"""Wave 128 — Parallel Universe Mapper.

Maps the topology of parallel universes — identifying which dimensions
are close, which are divergent, and which are in superposition. Creates
a navigable map of the multiverse.
"""
from __future__ import annotations

import hashlib
import math
import time
from typing import Any, Dict, List, Tuple


class UniverseNode:
    """A node representing a parallel universe."""

    def __init__(self, name: str, divergence: float = 0.0):
        self.name = name
        self.divergence = divergence
        self.x = 0.0
        self.y = 0.0
        self.connections: List[str] = []
        self.created = time.time()
        self.id = hashlib.sha256(f"universe:{name}".encode()).hexdigest()[:8]

    def distance_to(self, other: "UniverseNode") -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "divergence": round(self.divergence, 4),
                "position": [round(self.x, 4), round(self.y, 4)],
                "connections": len(self.connections)}


class ParallelUniverseMapper:
    """Maps the topology of parallel universes."""

    def __init__(self):
        self._universes: Dict[str, UniverseNode] = {}
        self._portals: List[Tuple[str, str]] = []

    def add_universe(self, name: str, divergence: float = 0.0) -> UniverseNode:
        node = UniverseNode(name, divergence)
        idx = len(self._universes)
        angle = idx * (2 * math.pi / max(idx + 1, 1))
        radius = 1.0 + divergence * 2
        node.x = radius * math.cos(angle)
        node.y = radius * math.sin(angle)
        self._universes[node.id] = node
        return node

    def open_portal(self, id_a: str, id_b: str) -> bool:
        a, b = self._universes.get(id_a), self._universes.get(id_b)
        if a and b:
            a.connections.append(id_b)
            b.connections.append(id_a)
            self._portals.append((id_a, id_b))
            return True
        return False

    def nearest_universe(self, name: str) -> Optional[Dict[str, Any]]:
        target = None
        for u in self._universes.values():
            if u.name == name:
                target = u
                break
        if not target:
            return None
        nearest = None
        min_dist = float("inf")
        for u in self._universes.values():
            if u.id == target.id:
                continue
            d = target.distance_to(u)
            if d < min_dist:
                min_dist = d
                nearest = u
        return nearest.to_dict() if nearest else None

    def get_universes(self) -> List[Dict[str, Any]]:
        return [u.to_dict() for u in self._universes.values()]

    def status(self) -> Dict[str, Any]:
        return {"total_universes": len(self._universes), "total_portals": len(self._portals)}
