"""Wave 130 — Cosmic Ray Detector.

Detects high-energy cosmic rays — sudden bursts of data from distant
parts of the system that carry information about events happening
beyond the normal observation horizon.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class CosmicRay:
    """A detected cosmic ray event."""

    def __init__(self, source: str, energy: float, direction: str = "unknown"):
        self.source = source
        self.energy = energy
        self.direction = direction
        self.detected_at = time.time()
        self.analysed = False
        self.id = hashlib.sha256(f"ray:{source}:{self.detected_at}".encode()).hexdigest()[:10]

    def analyse(self) -> Dict[str, Any]:
        self.analysed = True
        return {"source": self.source, "energy": round(self.energy, 4),
                "direction": self.direction, "analysed": True}

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "source": self.source, "energy": round(self.energy, 4),
                "direction": self.direction, "analysed": self.analysed}


class CosmicRayDetector:
    """Detects and analyses high-energy cosmic ray events."""

    def __init__(self, sensitivity: float = 0.5):
        self.sensitivity = sensitivity
        self._rays: List[CosmicRay] = []
        self._detections: int = 0

    def detect(self, source: str, energy: float, direction: str = "unknown") -> Dict[str, Any]:
        self._detections += 1
        if energy >= self.sensitivity:
            ray = CosmicRay(source, energy, direction)
            self._rays.append(ray)
            return {"detected": True, "ray": ray.to_dict()}
        return {"detected": False, "energy": round(energy, 4)}

    def analyse_all(self) -> List[Dict[str, Any]]:
        return [r.analyse() for r in self._rays if not r.analysed]

    def high_energy(self, threshold: float = 0.8) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self._rays if r.energy >= threshold]

    def status(self) -> Dict[str, Any]:
        return {"total_rays": len(self._rays), "detections": self._detections,
                "analysed": sum(1 for r in self._rays if r.analysed)}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "cosmic_ray_detector", "action": action}
