"""Wave 132 — Career Ladder.

Workers progress along a defined career ladder: each rung demands a
combination of reputation, skill mastery, and tasks completed.
Promotions reward workers with increased capacity and wage rate.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

LADDER = [
    ("intern", 0, 0.0, 0.5),
    ("junior", 5, 0.2, 0.9),
    ("associate", 15, 0.4, 1.3),
    ("senior", 30, 0.6, 1.8),
    ("lead", 50, 0.75, 2.4),
    ("principal", 80, 0.85, 3.2),
]


class CareerLadder:
    """Evaluates and advances workers along a career path."""

    def __init__(self):
        self._rungs: Dict[str, int] = {}
        self._task_counts: Dict[str, int] = {}
        self._wage_rates: Dict[str, float] = {}

    def register(self, worker: str) -> None:
        self._rungs.setdefault(worker, 0)
        self._task_counts.setdefault(worker, 0)
        self._wage_rates.setdefault(worker, LADDER[0][3])

    def record_task(self, worker: str, reputation: float = 0.0) -> Optional[str]:
        self.register(worker)
        self._task_counts[worker] += 1
        return self._recompute(worker, reputation)

    def _recompute(self, worker: str, reputation: float) -> Optional[str]:
        count = self._task_counts[worker]
        rung = self._rungs[worker]
        for index, (title, min_tasks, min_rep, wage) in enumerate(LADDER):
            if index > rung and count >= min_tasks and reputation >= min_rep:
                self._rungs[worker] = index
                self._wage_rates[worker] = wage
                return title
        return None

    def rung(self, worker: str) -> str:
        return LADDER[self._rungs.get(worker, 0)][0]

    def wage(self, worker: str) -> float:
        return self._wage_rates.get(worker, LADDER[0][3])

    def status(self) -> Dict[str, Any]:
        return {"workers": len(self._rungs),
                "leads": sum(1 for w in self._rungs if LADDER[self._rungs[w]][0] in ("lead", "principal")),
                "total_tasks": sum(self._task_counts.values())}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    ladder = CareerLadder()
    return {"status": "active", "module": "career_ladder",
            **ladder.status()}
