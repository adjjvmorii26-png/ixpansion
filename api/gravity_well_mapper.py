"""Wave 130 — Gravity Well Mapper.

Maps gravitational wells — deep attractors in the system that pull
modules and data toward them. Identifies black holes (data sinks),
stars (data sources), and orbital patterns around major attractors.
"""
from __future__ import annotations

import math
import time
from typing import Any, Dict, List


class GravityWell:
    """A gravitational attractor in the system."""

    def __init__(self, name: str, mass: float, x: float = 0.0, y: float = 0.0):
        self.name = name
        self.mass = mass
        self.x = x
        self.y = y
        self.orbiters: List[str] = []
        self.created = time.time()

    @property
    def well_type(self) -> str:
        if self.mass > 100:
            return "black_hole"
        elif self.mass > 10:
            return "star"
        elif self.mass > 1:
            return "planet"
        return "asteroid"

    def attract(self, other_name: str) -> str:
        self.orbiters.append(other_name)
        return other_name

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "mass": round(self.mass, 4), "type": self.well_type,
                "position": [round(self.x, 4), round(self.y, 4)],
                "orbiters": len(self.orbiters)}


class GravityWellMapper:
    """Maps gravitational wells and orbital patterns."""

    def __init__(self):
        self._wells: List[GravityWell] = []
        self._orbits: int = 0

    def place_well(self, name: str, mass: float, x: float = 0.0, y: float = 0.0) -> GravityWell:
        well = GravityWell(name, mass, x, y)
        self._wells.append(well)
        return well

    def orbit(self, well_name: str, orbiter: str) -> bool:
        for w in self._wells:
            if w.name == well_name:
                w.attract(orbiter)
                self._orbits += 1
                return True
        return False

    def strongest_well(self) -> Dict[str, Any]:
        if not self._wells:
            return {}
        return max(self._wells, key=lambda w: w.mass).to_dict()

    def get_wells(self) -> List[Dict[str, Any]]:
        return [w.to_dict() for w in self._wells]

    def status(self) -> Dict[str, Any]:
        return {"total_wells": len(self._wells), "total_orbits": self._orbits}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "gravity_well_mapper", "action": action}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "data", "status": "active", "wave": "130", "module": "gravity_well_mapper"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
