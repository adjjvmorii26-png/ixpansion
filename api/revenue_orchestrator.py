"""Wave 135 — Engagement Orchestrator.

The central ledger of the civilization's income: it aggregates every
engagement stream — marketplace fees, guild commissions, subscriptions,
royalties, sponsored experiments — into one consolidated engagement
pipeline and projects future cash flow from pipeline velocity.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class EngagementStream:
    """A single tracked income channel."""

    def __init__(self, name: str, kind: str, rate: float):
        self.name = name
        self.kind = kind
        self.rate = rate  # units per tick
        self.total = 0.0
        self.created = time.time()
        self.id = hashlib.sha256(f"revstream:{name}".encode()).hexdigest()[:10]

    def collect(self, multiplier: float = 1.0) -> float:
        amount = self.rate * multiplier
        self.total += amount
        return round(amount, 4)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "kind": self.kind,
                "rate": self.rate, "total": round(self.total, 4)}


class EngagementOrchestrator:
    """Aggregates and projects all civilization income."""

    def __init__(self):
        self._streams: Dict[str, EngagementStream] = {}
        self._pipeline_samples: List[float] = []
        self._collections = 0

    def register(self, name: str, kind: str, rate: float) -> EngagementStream:
        stream = EngagementStream(name, kind, rate)
        self._streams[stream.id] = stream
        return stream

    def collect_cycle(self, multiplier: float = 1.0) -> float:
        total = 0.0
        for stream in self._streams.values():
            total += stream.collect(multiplier)
        total = round(total, 4)
        self._pipeline_samples.append(total)
        self._collections += 1
        return total

    def projected_annualized(self) -> float:
        if not self._pipeline_samples:
            return 0.0
        avg = sum(self._pipeline_samples) / len(self._pipeline_samples)
        return round(avg * 365.0, 4)

    def engagement_breakdown(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self._streams.values()]

    def status(self) -> Dict[str, Any]:
        return {"streams": len(self._streams),
                "collections": self._collections,
                "pipeline_total": round(sum(self._pipeline_samples), 4),
                "projected_annualized": self.projected_annualized()}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    orchestrator = EngagementOrchestrator()
    return {"status": "active", "module": "engagement_orchestrator",
            **orchestrator.status()}
