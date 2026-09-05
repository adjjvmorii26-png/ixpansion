"""Wave 133 — Values Compass.

Defines the civilization's shared values and uses them to arbitrate
between competing policies. A value scoreboard tracks how closely
recent decisions align with declared principles, nudging drift back
toward the civilization's ethos.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

DEFAULT_VALUES = ["solidarity", "curiosity", "stewardship", "reciprocity", "adaptation"]


class ValuesCompass:
    """Declares and enforces the civilization's shared values."""

    def __init__(self):
        self._values: Dict[str, float] = {v: 0.5 for v in DEFAULT_VALUES}
        self._alignment_log: List[float] = []

    def adjust(self, value: str, delta: float) -> float:
        if value not in self._values:
            self._values[value] = 0.5
        self._values[value] = max(0.0, min(1.0, self._values[value] + delta))
        return self._values[value]

    def declare(self, values: Dict[str, float]) -> None:
        for name, strength in values.items():
            self._values[name] = max(0.0, min(1.0, strength))

    def arbitrate(self, option_a: str, option_b: str, value: str) -> str:
        """Pick the option whose semantic weight is favored by the value."""
        weight = self._values.get(value, 0.5)
        return option_a if weight >= 0.5 else option_b

    def record_decision(self, aligned: bool) -> float:
        score = 1.0 if aligned else 0.0
        self._alignment_log.append(score)
        return round(sum(self._alignment_log) / len(self._alignment_log), 4)

    def status(self) -> Dict[str, Any]:
        return {"values": dict(self._values),
                "decisions_aligned": round(
                    (sum(self._alignment_log) / len(self._alignment_log)) if self._alignment_log else 1.0, 4),
                "decisions": len(self._alignment_log)}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    compass = ValuesCompass()
    return {"status": "active", "module": "values_compass",
            **compass.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "organ", "status": "active", "wave": "133", "module": "values_compass"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
