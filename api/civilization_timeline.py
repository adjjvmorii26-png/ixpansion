"""Wave 133 — Civilization Timeline.

A living chronicle of the workforce civilization: epochs marked by
milestones (foundings, crises, golden ages) are recorded so the
civilization can reflect on its own history and learn from cycles.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class Epoch:
    """A marked era in the civilization timeline."""

    def __init__(self, name: str, kind: str, description: str):
        self.name = name
        self.kind = kind
        self.description = description
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"epoch:{name}".encode()).hexdigest()[:10]

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "kind": self.kind,
                "description": self.description, "timestamp": round(self.timestamp, 4)}


class CivilizationTimeline:
    """Records and queries the civilization's epoch history."""

    def __init__(self):
        self._epochs: List[Epoch] = []
        self._kind_counts: Dict[str, int] = {}

    def mark(self, name: str, kind: str, description: str = "") -> Epoch:
        epoch = Epoch(name, kind, description)
        self._epochs.append(epoch)
        self._kind_counts[kind] = self._kind_counts.get(kind, 0) + 1
        return epoch

    def by_kind(self, kind: str) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self._epochs if e.kind == kind]

    def timeline(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in sorted(self._epochs, key=lambda e: e.timestamp)]

    def current_era(self) -> str:
        if not self._epochs:
            return "prehistory"
        return self._epochs[-1].name

    def status(self) -> Dict[str, Any]:
        return {"epochs": len(self._epochs), "kinds": dict(self._kind_counts),
                "era": self.current_era()}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    timeline = CivilizationTimeline()
    return {"status": "active", "module": "civilization_timeline",
            **timeline.status()}


def coherence_vitals() -> dict:
    """civilization_timeline reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "civilization_timeline_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['workforce_nexus', 'worker_wellness', 'system_pulse']

