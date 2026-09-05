"""Wave 124 — Kairos Detector.

Detects kairos moments — opportune instants where the right action at
the right time produces disproportionate impact. The system monitors
temporal pressure gradients to identify these critical junctures.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class KairosMoment:
    """A detected opportune instant."""

    def __init__(self, context: str, pressure: float, window: float = 60.0):
        self.context = context
        self.pressure = pressure
        self.window = window
        self.detected_at = time.time()
        self.expired = False
        self.seized = False
        self.id = hashlib.sha256(f"kairos:{context}:{self.detected_at}".encode()).hexdigest()[:10]

    def seize(self) -> Dict[str, Any]:
        self.seized = True
        return {"context": self.context, "seized": True, "pressure": round(self.pressure, 4)}

    def check_expiry(self) -> bool:
        if time.time() - self.detected_at > self.window:
            self.expired = True
        return self.expired

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "context": self.context,
                "pressure": round(self.pressure, 4), "seized": self.seized,
                "expired": self.expired}


class KairosDetector:
    """Monitors for opportune temporal moments."""

    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self._moments: List[KairosMoment] = []
        self._seized_count = 0

    def scan(self, context: str, pressure: float, window: float = 60.0) -> Dict[str, Any]:
        moment = KairosMoment(context, pressure, window)
        self._moments.append(moment)
        if pressure >= self.threshold:
            return {"detected": True, "moment": moment.to_dict()}
        return {"detected": False, "pressure": round(pressure, 4)}

    def seize_moment(self, moment_id: str) -> Dict[str, Any]:
        for m in self._moments:
            if m.id == moment_id:
                result = m.seize()
                self._seized_count += 1
                return result
        return {"error": "moment not found"}

    def active_moments(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self._moments if not m.expired and not m.seized]

    def status(self) -> Dict[str, Any]:
        return {"total_moments": len(self._moments), "seized": self._seized_count,
                "active": len(self.active_moments())}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "kairos_detector", "action": action}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "protocol", "status": "active", "wave": "124", "module": "kairos_detector"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
