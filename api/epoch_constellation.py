"""Wave 124 — Epoch Constellation.

Maps historical epochs as constellations in the night sky of time —
each epoch is a star, and the patterns between them reveal the
underlying rhythm of history.
"""
from __future__ import annotations

import hashlib
import math
import time
from typing import Any, Dict, List, Tuple


class EpochStar:
    """A star representing a historical epoch."""

    def __init__(self, name: str, start: float, end: float, intensity: float = 1.0):
        self.name = name
        self.start = start
        self.end = end
        self.intensity = intensity
        self.x = 0.0
        self.y = 0.0
        self.id = hashlib.sha256(f"epoch:{name}".encode()).hexdigest()[:8]

    @property
    def duration(self) -> float:
        return self.end - self.start

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "start": self.start, "end": self.end,
                "duration": round(self.duration, 4), "intensity": round(self.intensity, 4)}


class EpochConstellation:
    """Maps epochs as stellar constellations."""

    def __init__(self):
        self._stars: Dict[str, EpochStar] = {}
        self._connections: List[Tuple[str, str]] = []

    def add_epoch(self, name: str, start: float, end: float, intensity: float = 1.0) -> EpochStar:
        star = EpochStar(name, start, end, intensity)
        idx = len(self._stars)
        angle = idx * (2 * math.pi / max(idx + 1, 1))
        radius = 1.0 + idx * 0.15
        star.x = radius * math.cos(angle)
        star.y = radius * math.sin(angle)
        self._stars[star.id] = star
        return star

    def connect_epochs(self, id_a: str, id_b: str) -> bool:
        if id_a in self._stars and id_b in self._stars:
            self._connections.append((id_a, id_b))
            return True
        return False

    def longest_epoch(self) -> Dict[str, Any]:
        if not self._stars:
            return {}
        star = max(self._stars.values(), key=lambda s: s.duration)
        return star.to_dict()

    def brightest_epoch(self) -> Dict[str, Any]:
        if not self._stars:
            return {}
        star = max(self._stars.values(), key=lambda s: s.intensity)
        return star.to_dict()

    def get_stars(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self._stars.values()]

    def status(self) -> Dict[str, Any]:
        return {"total_epochs": len(self._stars), "total_connections": len(self._connections)}
