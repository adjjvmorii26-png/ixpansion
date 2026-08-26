"""Wave 130 — Stellar Compass.

A compass that navigates by stellar patterns — using the positions of
digital constellations to find optimal paths through the codebase,
like ancient navigators used the stars.
"""
from __future__ import annotations

import hashlib
import math
import time
from typing import Any, Dict, List, Optional


class Star:
    """A digital star for navigation."""

    def __init__(self, name: str, x: float, y: float, magnitude: float = 1.0):
        self.name = name
        self.x = x
        self.y = y
        self.magnitude = magnitude
        self.id = hashlib.sha256(f"star:{name}".encode()).hexdigest()[:8]

    def distance_to(self, other: "Star") -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "x": round(self.x, 4),
                "y": round(self.y, 4), "magnitude": round(self.magnitude, 4)}


class StellarCompass:
    """Navigates using digital stellar patterns."""

    def __init__(self):
        self._stars: Dict[str, Star] = {}
        self._navigations: List[Dict[str, Any]] = []

    def chart_star(self, name: str, x: float, y: float, magnitude: float = 1.0) -> Star:
        star = Star(name, x, y, magnitude)
        self._stars[star.id] = star
        return star

    def navigate(self, start_name: str, end_name: str) -> Optional[Dict[str, Any]]:
        start = next((s for s in self._stars.values() if s.name == start_name), None)
        end = next((s for s in self._stars.values() if s.name == end_name), None)
        if not start or not end:
            return None
        distance = start.distance_to(end)
        bearing = math.atan2(end.y - start.y, end.x - start.x)
        result = {"from": start_name, "to": end_name, "distance": round(distance, 4),
                  "bearing_degrees": round(math.degrees(bearing), 2)}
        self._navigations.append(result)
        return result

    def nearest_star(self, x: float, y: float) -> Optional[Dict[str, Any]]:
        if not self._stars:
            return None
        nearest = min(self._stars.values(), key=lambda s: math.sqrt((s.x-x)**2 + (s.y-y)**2))
        return nearest.to_dict()

    def constellation(self, names: List[str]) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self._stars.values() if s.name in names]

    def status(self) -> Dict[str, Any]:
        return {"total_stars": len(self._stars), "navigations": len(self._navigations)}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "stellar_compass", "action": action}
