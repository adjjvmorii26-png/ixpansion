"""Wave 129 — Semantic Precipitate.

When meaning becomes supersaturated, it precipitates out as solid
knowledge structures. This module manages the crystallisation of
liquid understanding into solid, reusable knowledge.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class Crystal:
    """A precipitated knowledge crystal."""

    def __init__(self, name: str, solution: str, saturation: float):
        self.name = name
        self.solution = solution
        self.saturation = saturation
        self.facets: List[str] = []
        self.created = time.time()
        self.id = hashlib.sha256(f"crystal:{name}".encode()).hexdigest()[:10]

    def grow(self, facet: str) -> int:
        self.facets.append(facet)
        return len(self.facets)

    def dissolve(self) -> float:
        self.saturation = max(0.0, self.saturation - 0.3)
        return self.saturation

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "saturation": round(self.saturation, 4),
                "facets": len(self.facets)}


class SemanticPrecipitate:
    """Manages crystallisation of meaning into knowledge."""

    def __init__(self, supersaturation_threshold: float = 0.7):
        self.threshold = supersaturation_threshold
        self._crystals: List[Crystal] = []
        self._precipitate_count = 0

    def supersaturate(self, name: str, solution: str, saturation: float) -> Dict[str, Any]:
        if saturation >= self.threshold:
            crystal = Crystal(name, solution, saturation)
            self._crystals.append(crystal)
            self._precipitate_count += 1
            return {"precipitated": True, "crystal": crystal.to_dict()}
        return {"precipitated": False, "saturation": saturation}

    def grow_crystal(self, crystal_id: str, facet: str) -> bool:
        for c in self._crystals:
            if c.id == crystal_id:
                c.grow(facet)
                return True
        return False

    def get_crystals(self) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self._crystals]

    def status(self) -> Dict[str, Any]:
        return {"total_crystals": len(self._crystals),
                "precipitate_events": self._precipitate_count}
