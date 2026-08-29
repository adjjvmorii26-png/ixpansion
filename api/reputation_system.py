"""Wave 132 — Reputation System.

Workers build reputation from delivered task quality, peer reviews,
and participation in the collaboration hub. High reputation unlocks
trust tiers that gate sensitive assignments and premium payouts.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

TRUST_TIERS = ["newcomer", "established", "trusted", "venerated"]


class ReputationSystem:
    """Tracks trust and reputation for the workforce."""

    def __init__(self):
        self._reputation: Dict[str, float] = {}
        self._events: Dict[str, List[float]] = {}

    def register(self, worker: str, initial: float = 0.0) -> None:
        self._reputation[worker] = max(0.0, min(1.0, initial))
        self._events.setdefault(worker, [])

    def reward(self, worker: str, amount: float) -> float:
        if worker not in self._reputation:
            self.register(worker)
        self._reputation[worker] = max(0.0, min(1.0, self._reputation[worker] + amount))
        self._events[worker].append(amount)
        return self._reputation[worker]

    def penalize(self, worker: str, amount: float) -> float:
        if worker not in self._reputation:
            self.register(worker)
        self._reputation[worker] = max(0.0, self._reputation[worker] - amount)
        self._events[worker].append(-amount)
        return self._reputation[worker]

    def tier(self, worker: str) -> str:
        rep = self._reputation.get(worker, 0.0)
        idx = min(int(rep * len(TRUST_TIERS)), len(TRUST_TIERS) - 1)
        return TRUST_TIERS[idx]

    def can_trust(self, worker: str, min_tier: str) -> bool:
        tiers = TRUST_TIERS
        return tiers.index(self.tier(worker)) >= tiers.index(min_tier)

    def status(self) -> Dict[str, Any]:
        return {"workers": len(self._reputation),
                "venerated": sum(1 for w in self._reputation if self.tier(w) == "venerated"),
                "trusted": sum(1 for w in self._reputation if self.tier(w) in ("trusted", "venerated"))}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    system = ReputationSystem()
    return {"status": "active", "module": "reputation_system",
            **system.status()}
