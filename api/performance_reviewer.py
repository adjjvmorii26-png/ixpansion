"""Wave 131 — Performance Reviewer.

Evaluates worker performance over rolling windows, computes composite
scores, and issues promotions when workers consistently outperform
their cohort. Promotions unlock new task tiers and higher capacity.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class ReviewRecord:
    """A single performance evaluation for a worker."""

    def __init__(self, worker: str, quality: float, throughput: float):
        self.worker = worker
        self.quality = quality
        self.throughput = throughput
        self.score = round(0.6 * quality + 0.4 * throughput, 4)
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {"worker": self.worker, "quality": self.quality,
                "throughput": self.throughput, "score": self.score}


class PerformanceReviewer:
    """Tracks and evaluates worker performance for promotions."""

    TIERS = ["trainee", "contributor", "senior", "lead", "architect"]

    def __init__(self):
        self._records: Dict[str, List[ReviewRecord]] = {}
        self._tiers: Dict[str, int] = {}
        self._promotions = 0

    def register(self, worker: str) -> None:
        if worker not in self._records:
            self._records[worker] = []
            self._tiers[worker] = 0

    def review(self, worker: str, quality: float, throughput: float) -> ReviewRecord:
        self.register(worker)
        record = ReviewRecord(worker, quality, throughput)
        self._records[worker].append(record)
        if self._composite(worker) >= 0.75 and self._tiers[worker] < len(self.TIERS) - 1:
            self._tiers[worker] += 1
            self._promotions += 1
        return record

    def _composite(self, worker: str) -> float:
        recent = self._records[worker][-5:]
        if not recent:
            return 0.0
        return round(sum(r.score for r in recent) / len(recent), 4)

    def tier(self, worker: str) -> str:
        return self.TIERS[self._tiers.get(worker, 0)]

    def promote(self, worker: str) -> bool:
        self.register(worker)
        if self._tiers[worker] >= len(self.TIERS) - 1:
            return False
        self._tiers[worker] += 1
        self._promotions += 1
        return True

    def report(self, worker: Optional[str] = None) -> Dict[str, Any]:
        if worker is not None:
            return {"worker": worker, "tier": self.tier(worker),
                    "composite_score": self._composite(worker),
                    "reviews": len(self._records.get(worker, []))}
        return {"workers": len(self._records), "tiers": dict(self._tiers),
                "promotions": self._promotions}

    def status(self) -> Dict[str, Any]:
        return self.report()


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    reviewer = PerformanceReviewer()
    return {"status": "active", "module": "performance_reviewer",
            **reviewer.status()}
