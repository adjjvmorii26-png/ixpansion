"""Wave 122 — Dream Constellation.

Maps dreams as constellations in the mental sky — connecting dream
fragments with lines of meaning, creating celestial patterns that
reveal the deeper structure of the system's imagination.
"""
from __future__ import annotations

import hashlib
import math
import time
from typing import Any, Dict, List, Tuple


class DreamStar:
    """A single dream star in the constellation."""

    def __init__(self, name: str, brightness: float = 1.0):
        self.name = name
        self.brightness = brightness
        self.x = 0.0
        self.y = 0.0
        self.created = time.time()
        self.id = hashlib.sha256(f"star:{name}".encode()).hexdigest()[:8]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "brightness": round(self.brightness, 4),
            "x": round(self.x, 4),
            "y": round(self.y, 4),
        }


class DreamConstellation:
    """Maps and arranges dream stars into constellations."""

    def __init__(self):
        self._stars: Dict[str, DreamStar] = {}
        self._connections: List[Tuple[str, str]] = []
        self._constellation_count = 0

    def add_star(self, name: str, brightness: float = 1.0) -> DreamStar:
        star = DreamStar(name, brightness)
        angle = len(self._stars) * (2 * math.pi / max(len(self._stars) + 1, 1))
        radius = 1.0 + len(self._stars) * 0.1
        star.x = radius * math.cos(angle)
        star.y = radius * math.sin(angle)
        self._stars[star.id] = star
        return star

    def connect(self, star_a: str, star_b: str) -> bool:
        a = self._stars.get(star_a)
        b = self._stars.get(star_b)
        if not a or not b:
            return False
        self._connections.append((star_a, star_b))
        return True

    def constellation_pattern(self) -> Dict[str, Any]:
        self._constellation_count += 1
        return {
            "stars": len(self._stars),
            "connections": len(self._connections),
            "pattern_id": self._constellation_count,
            "brightness": sum(s.brightness for s in self._stars.values()),
        }

    def get_stars(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self._stars.values()]

    def status(self) -> Dict[str, Any]:
        return {
            "total_stars": len(self._stars),
            "total_connections": len(self._connections),
            "constellations_formed": self._constellation_count,
        }
