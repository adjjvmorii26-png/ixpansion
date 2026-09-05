"""Wave 125 — Neural Vine.

Growing neural connections that spread like vines through the codebase,
seeking light (data) and forming new pathways where none existed before.
Each vine grows toward information density.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class VineSegment:
    """A segment of a neural vine."""

    def __init__(self, origin: str, direction: str, length: float = 1.0):
        self.origin = origin
        self.direction = direction
        self.length = length
        self.thickness = 0.1
        self.leaves: List[str] = []
        self.created = time.time()

    def grow(self, amount: float) -> float:
        self.length += amount
        self.thickness = min(1.0, self.thickness + 0.01)
        return self.length

    def sprout_leaf(self, data_label: str) -> str:
        self.leaves.append(data_label)
        return data_label

    def to_dict(self) -> Dict[str, Any]:
        return {"origin": self.origin, "direction": self.direction,
                "length": round(self.length, 4), "thickness": round(self.thickness, 4),
                "leaves": len(self.leaves)}


class NeuralVine:
    """A growing neural vine network."""

    def __init__(self, name: str):
        self.name = name
        self.segments: List[VineSegment] = []
        self.total_growth = 0.0

    def grow_toward(self, direction: str, data_density: float = 0.5) -> VineSegment:
        seg = VineSegment(self.name, direction, length=data_density * 2)
        self.segments.append(seg)
        self.total_growth += seg.length
        return seg

    def branch(self, parent_idx: int, new_direction: str) -> Optional[VineSegment]:
        if parent_idx < 0 or parent_idx >= len(self.segments):
            return None
        parent = self.segments[parent_idx]
        child = VineSegment(parent.origin, new_direction, length=0.5)
        self.segments.append(child)
        self.total_growth += child.length
        return child

    def total_length(self) -> float:
        return sum(s.length for s in self.segments)

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "segments": len(self.segments),
                "total_length": round(self.total_length(), 4)}


class NeuralVineNetwork:
    """Manages a network of growing neural vines."""

    def __init__(self):
        self._vines: Dict[str, NeuralVine] = {}
        self._growth_cycles = 0

    def plant(self, name: str) -> NeuralVine:
        vine = NeuralVine(name)
        self._vines[name] = vine
        return vine

    def grow_cycle(self) -> int:
        total_growth = 0
        for vine in self._vines.values():
            vine.grow_toward("forward", data_density=0.5)
            total_growth += 1
        self._growth_cycles += 1
        return total_growth

    def status(self) -> Dict[str, Any]:
        total_segments = sum(len(v.segments) for v in self._vines.values())
        return {"total_vines": len(self._vines), "total_segments": total_segments,
                "growth_cycles": self._growth_cycles}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "neural_vine", "action": action}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "data", "status": "active", "wave": "125", "module": "neural_vine"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
