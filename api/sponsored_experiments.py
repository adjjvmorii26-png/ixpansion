"""Wave 127 — Sponsored Experiments.

Modules can sponsor experiments — funding risky but potentially
high-reward module development. The sponsor receives a percentage of
the experimental module's success, creating a venture capital model
for code evolution.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class Experiment:
    """A sponsored experiment."""

    def __init__(self, name: str, sponsor: str, funding: float):
        self.name = name
        self.sponsor = sponsor
        self.funding = funding
        self.created = time.time()
        self.success = False
        self.returns = 0.0
        self.id = hashlib.sha256(f"exp:{name}".encode()).hexdigest()[:8]

    def conclude(self, was_success: bool, returns: float = 0.0) -> Dict[str, Any]:
        self.success = was_success
        self.returns = returns
        return {"name": self.name, "sponsor": self.sponsor,
                "success": was_success, "funding": self.funding,
                "returns": round(returns, 4)}

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "sponsor": self.sponsor,
                "funding": self.funding, "success": self.success,
                "returns": round(self.returns, 4)}


class SponsoredExperimentsEngine:
    """Manages sponsored experimental modules."""

    def __init__(self):
        self._experiments: List[Experiment] = []
        self._total_funding = 0.0
        self._total_returns = 0.0

    def sponsor(self, name: str, sponsor: str, funding: float) -> Experiment:
        exp = Experiment(name, sponsor, funding)
        self._experiments.append(exp)
        self._total_funding += funding
        return exp

    def conclude(self, experiment_id: str, success: bool, returns: float = 0.0) -> Dict[str, Any]:
        for exp in self._experiments:
            if exp.id == experiment_id:
                result = exp.conclude(success, returns)
                self._total_returns += returns
                return result
        return {"error": "experiment not found"}

    def roi(self) -> float:
        if self._total_funding == 0:
            return 0.0
        return self._total_returns / self._total_funding

    def status(self) -> Dict[str, Any]:
        successful = sum(1 for e in self._experiments if e.success)
        return {"total_experiments": len(self._experiments), "successful": successful,
                "total_funding": round(self._total_funding, 4),
                "total_returns": round(self._total_returns, 4),
                "roi": round(self.roi(), 4)}
