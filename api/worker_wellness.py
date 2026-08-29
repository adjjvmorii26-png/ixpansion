"""Wave 134 — Worker Wellness.

Monitors worker health signals — task load, rest gaps, reputation
stress — and issues burnout alerts. Regenerative actions (rest,
rotation, mentorship) restore wellness so the workforce sustains
itself instead of degrading.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class WorkerWellness:
    """Tracks and restores worker wellness."""

    def __init__(self):
        self._wellness: Dict[str, float] = {}
        self._load: Dict[str, float] = {}
        self._alerts: List[str] = []

    def register(self, worker: str, initial: float = 1.0) -> None:
        self._wellness[worker] = max(0.0, min(1.0, initial))
        self._load[worker] = 0.0

    def work(self, worker: str, load_amount: float = 0.1) -> float:
        self.register(worker)
        self._load[worker] += load_amount
        strain = load_amount * self._load[worker]
        self._wellness[worker] = max(0.0, self._wellness[worker] - strain)
        if self._wellness[worker] < 0.3:
            alert = f"burnout:{worker}"
            if alert not in self._alerts:
                self._alerts.append(alert)
        return self._wellness[worker]

    def rest(self, worker: str, recovery: float = 0.2) -> None:
        self.register(worker)
        self._wellness[worker] = min(1.0, self._wellness[worker] + recovery)
        self._load[worker] = max(0.0, self._load[worker] - recovery)

    def rotate(self, worker: str, to_role: str = "advisor") -> None:
        self.register(worker)
        self._wellness[worker] = min(1.0, self._wellness[worker] + 0.1)

    def at_risk(self) -> List[str]:
        return [w for w, v in self._wellness.items() if v < 0.3]

    def status(self) -> Dict[str, Any]:
        return {"workers": len(self._wellness),
                "avg_wellness": round(
                    (sum(self._wellness.values()) / len(self._wellness)) if self._wellness else 1.0, 4),
                "alerts": len(self._alerts),
                "at_risk": len(self.at_risk())}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    wellness = WorkerWellness()
    return {"status": "active", "module": "worker_wellness",
            **wellness.status()}
