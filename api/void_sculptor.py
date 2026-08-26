"""Wave 121 — Void Sculptor.

Sculpts meaningful structures from pure absence and negative space.
Where other modules create by adding, the Void Sculptor creates by
removing — discovering what remains when everything unnecessary is
stripped away.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class VoidShape:
    """A shape defined by what has been removed."""

    def __init__(self, name: str, material: List[str]):
        self.name = name
        self.material = list(material)
        self.removed: List[str] = []
        self.created = time.time()
        self.beauty_score = 0.0

    def carve(self, element: str) -> bool:
        if element in self.material:
            self.material.remove(element)
            self.removed.append(element)
            self.beauty_score += 1.0 / max(len(self.material), 1)
            return True
        return False

    def carve_until(self, remaining: int) -> int:
        carved = 0
        while len(self.material) > remaining and self.material:
            self.carve(self.material[0])
            carved += 1
        return carved

    @property
    def emptiness(self) -> float:
        total = len(self.material) + len(self.removed)
        return len(self.removed) / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "material_remaining": len(self.material),
            "removed": len(self.removed),
            "emptiness": round(self.emptiness, 4),
            "beauty_score": round(self.beauty_score, 4),
        }


class VoidSculptor:
    """Creates meaning through strategic removal."""

    def __init__(self):
        self._shapes: List[VoidShape] = []
        self._carvings: List[Dict[str, Any]] = []

    def begin_sculpture(self, name: str, material: List[str]) -> VoidShape:
        shape = VoidShape(name, material)
        self._shapes.append(shape)
        return shape

    def deep_carve(self, shape: VoidShape, depth: int = 3) -> int:
        carved = 0
        for _ in range(depth):
            if shape.material:
                shape.carve(shape.material[0])
                carved += 1
        return carved

    def find_beauty(self, shape: VoidShape) -> Dict[str, Any]:
        result = {
            "name": shape.name,
            "beauty_score": round(shape.beauty_score, 4),
            "emptiness": round(shape.emptiness, 4),
            "sculpted_at": time.time(),
        }
        self._carvings.append(result)
        return result

    def get_shapes(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self._shapes]

    def status(self) -> Dict[str, Any]:
        total_removed = sum(len(s.removed) for s in self._shapes)
        return {
            "total_sculptures": len(self._shapes),
            "total_carvings": len(self._carvings),
            "total_elements_removed": total_removed,
        }
