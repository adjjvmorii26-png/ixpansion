"""Wave 134 — Self-Improvement Loop.

Workers propose improvements to their own routines, tools, and
templates. Each proposal is graded on estimated impact and risk; safe
high-value ideas are auto-installed into the civilization, while
risky ones enter a review queue.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class ImprovementProposal:
    """A worker's suggestion for making the civilization better."""

    def __init__(self, author: str, title: str, impact: float, risk: float):
        self.author = author
        self.title = title
        self.impact = max(0.0, min(1.0, impact))
        self.risk = max(0.0, min(1.0, risk))
        self.status = "pending"
        self.score = round(self.impact - self.risk, 4)
        self.created = time.time()
        self.id = hashlib.sha256(f"improve:{title}".encode()).hexdigest()[:10]

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "author": self.author, "title": self.title,
                "impact": self.impact, "risk": self.risk, "score": self.score,
                "status": self.status}


class SelfImprovementLoop:
    """Auto-installs safe high-value improvements."""

    def __init__(self, risk_threshold: float = 0.45):
        self.risk_threshold = risk_threshold
        self._proposals: Dict[str, ImprovementProposal] = {}
        self._installed = 0
        self._queued = 0

    def propose(self, author: str, title: str, impact: float, risk: float) -> ImprovementProposal:
        proposal = ImprovementProposal(author, title, impact, risk)
        self._proposals[proposal.id] = proposal
        if risk <= self.risk_threshold:
            proposal.status = "installed"
            self._installed += 1
        else:
            proposal.status = "review"
            self._queued += 1
        return proposal

    def approve(self, proposal_id: str) -> bool:
        proposal = self._proposals.get(proposal_id)
        if proposal is None or proposal.status != "review":
            return False
        proposal.status = "installed"
        self._installed += 1
        self._queued = max(0, self._queued - 1)
        return True

    def reject(self, proposal_id: str) -> bool:
        proposal = self._proposals.get(proposal_id)
        if proposal is None or proposal.status != "review":
            return False
        proposal.status = "rejected"
        self._queued = max(0, self._queued - 1)
        return True

    def status(self) -> Dict[str, Any]:
        return {"proposals": len(self._proposals), "installed": self._installed,
                "review_queue": self._queued}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    loop = SelfImprovementLoop()
    return {"status": "active", "module": "self_improvement_loop",
            **loop.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "protocol", "status": "active", "wave": "134", "module": "self_improvement_loop"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
