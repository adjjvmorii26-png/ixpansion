"""Wave 124 — Time Dilation Mapper.

Maps regions where time flows faster or slower — detecting temporal
dilation events where the system experiences subjective time differently
from objective time.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class DilationZone:
    """A region where time flows at a different rate."""

    def __init__(self, name: str, dilation_factor: float = 1.0):
        self.name = name
        self.dilation_factor = dilation_factor
        self.created = time.time()
        self.events: List[Dict[str, Any]] = []

    def enter(self) -> Dict[str, Any]:
        event = {"zone": self.name, "factor": self.dilation_factor,
                 "entered_at": time.time()}
        self.events.append(event)
        return event

    def subjective_duration(self, objective_seconds: float) -> float:
        return objective_seconds * self.dilation_factor

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "dilation_factor": round(self.dilation_factor, 4),
                "entries": len(self.events)}


class TimeDilationMapper:
    """Maps and tracks temporal dilation across the system."""

    def __init__(self):
        self._zones: Dict[str, DilationZone] = {}
        self._readings: List[Dict[str, Any]] = []

    def register_zone(self, name: str, factor: float = 1.0) -> DilationZone:
        zone = DilationZone(name, factor)
        self._zones[name] = zone
        return zone

    def enter_zone(self, name: str) -> Dict[str, Any]:
        zone = self._zones.get(name)
        if not zone:
            return {"error": f"Zone '{name}' not found"}
        return zone.enter()

    def measure(self, zone_name: str, objective_seconds: float) -> Dict[str, Any]:
        zone = self._zones.get(zone_name)
        if not zone:
            return {"error": "zone not found"}
        subjective = zone.subjective_duration(objective_seconds)
        result = {"zone": zone_name, "objective": objective_seconds,
                  "subjective": round(subjective, 4), "factor": zone.dilation_factor}
        self._readings.append(result)
        return result

    def fastest_zone(self) -> Optional[str]:
        if not self._zones:
            return None
        return max(self._zones.values(), key=lambda z: z.dilation_factor).name

    def slowest_zone(self) -> Optional[str]:
        if not self._zones:
            return None
        return min(self._zones.values(), key=lambda z: z.dilation_factor).name

    def status(self) -> Dict[str, Any]:
        return {"total_zones": len(self._zones), "total_readings": len(self._readings)}
