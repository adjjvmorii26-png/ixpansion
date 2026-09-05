"""Wave 137 — Resilience Engine.

Models the civilization's ability to withstand and absorb shocks.
Each subsystem is assigned a resilience rating and redundancy; the
engine computes an overall resilience score and identifies which
single points of failure would cascade if hit.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class Subsystem:
    """A tracked subsystem with resilience properties."""

    def __init__(self, name: str, redundancy: int, load: float = 0.5):
        self.name = name
        self.redundancy = max(1, redundancy)
        self.load = max(0.0, min(1.0, load))
        self.created = time.time()
        self.id = hashlib.sha256(f"sub:{name}".encode()).hexdigest()[:10]

    def resilience(self) -> float:
        base = 1.0 - self.load
        bonus = min(0.4, (self.redundancy - 1) * 0.2)
        return round(min(1.0, base + bonus), 4)

    def single_point_of_failure(self) -> bool:
        return self.redundancy == 1 and self.load > 0.7

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "redundancy": self.redundancy,
                "load": self.load, "resilience": self.resilience(),
                "spof": self.single_point_of_failure()}


class ResilienceEngine:
    """Computes and improves civilization-wide resilience."""

    def __init__(self):
        self._subsystems: Dict[str, Subsystem] = {}

    def add(self, name: str, redundancy: int = 1, load: float = 0.5) -> Subsystem:
        subsystem = Subsystem(name, redundancy, load)
        self._subsystems[subsystem.id] = subsystem
        return subsystem

    def overall_resilience(self) -> float:
        if not self._subsystems:
            return 1.0
        return round(sum(s.resilience() for s in self._subsystems.values())
                     / len(self._subsystems), 4)

    def spofs(self) -> List[str]:
        return [s.name for s in self._subsystems.values() if s.single_point_of_failure()]

    def harden(self, subsystem_id: str) -> bool:
        subsystem = self._subsystems.get(subsystem_id)
        if subsystem is None:
            return False
        subsystem.redundancy += 1
        subsystem.load = max(0.0, subsystem.load - 0.1)
        return True

    def status(self) -> Dict[str, Any]:
        return {"subsystems": len(self._subsystems),
                "overall_resilience": self.overall_resilience(),
                "fragile": self.spofs()}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    engine = ResilienceEngine()
    return {"status": "active", "module": "resilience_engine",
            **engine.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "protocol", "status": "active", "wave": "137", "module": "resilience_engine"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
