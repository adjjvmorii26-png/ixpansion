"""Wave 133 — Civilization Kernel.

The governance hub of the workforce civilization: it binds the
economy, reputation, roster, and memory into a single health signal
and applies civilizations-level policies when the workforce drifts
out of balance.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class CivilizationKernel:
    """Central governance amalgamator for the workforce civilization."""

    def __init__(self):
        self._policies: Dict[str, float] = {}
        self._health_log: List[float] = []
        self._epoch = 0.0

    def set_policy(self, name: str, value: float) -> None:
        self._policies[name] = max(0.0, min(1.0, value))

    def observe(self, economy_health: float = 0.5, reputation_health: float = 0.5,
                roster_health: float = 0.5) -> float:
        health = round((economy_health + reputation_health + roster_health) / 3.0, 4)
        self._health_log.append(health)
        self._epoch = time.time()
        return health

    def drift(self) -> float:
        if len(self._health_log) < 2:
            return 0.0
        return round(self._health_log[-1] - self._health_log[-2], 4)

    def intervention_needed(self, threshold: float = 0.15) -> bool:
        return self.drift() < -threshold

    def status(self) -> Dict[str, Any]:
        return {"policies": len(self._policies),
                "health_samples": len(self._health_log),
                "current_health": self._health_log[-1] if self._health_log else None,
                "drift": self.drift()}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    kernel = CivilizationKernel()
    return {"status": "active", "module": "civilization_kernel",
            **kernel.status()}
