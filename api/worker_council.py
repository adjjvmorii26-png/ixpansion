"""Wave 133 — Worker Council.

A participatory governance body. Workers submit proposals, the
council debates via weighted votes (weight = reputation), and passed
proposals become binding policies for the civilization.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class Proposal:
    """A proposal submitted to the worker council."""

    def __init__(self, title: str, author: str, text: str):
        self.title = title
        self.author = author
        self.text = text
        self.votes_for = 0.0
        self.votes_against = 0.0
        self.status = "draft"
        self.created = time.time()
        self.id = hashlib.sha256(f"prop:{title}".encode()).hexdigest()[:10]

    def vote(self, weight: float, in_favor: bool) -> None:
        if in_favor:
            self.votes_for += weight
        else:
            self.votes_against += weight

    def outcome(self) -> str:
        if self.votes_for + self.votes_against == 0:
            return "unvoted"
        if self.votes_for > self.votes_against:
            return "passed"
        return "rejected"

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "title": self.title, "author": self.author,
                "votes_for": round(self.votes_for, 4),
                "votes_against": round(self.votes_against, 4),
                "status": self.outcome()}


class WorkerCouncil:
    """Votes on proposals with reputation-weighted ballots."""

    def __init__(self):
        self._proposals: Dict[str, Proposal] = {}
        self._reputations: Dict[str, float] = {}
        self._passed = 0

    def submit(self, title: str, author: str, text: str) -> Proposal:
        proposal = Proposal(title, author, text)
        self._proposals[proposal.id] = proposal
        return proposal

    def set_reputation(self, worker: str, value: float) -> None:
        self._reputations[worker] = max(0.0, min(1.0, value))

    def vote(self, proposal_id: str, voter: str, in_favor: bool) -> bool:
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            return False
        weight = self._reputations.get(voter, 0.5)
        proposal.vote(weight, in_favor)
        return True

    def tally(self, proposal_id: str) -> str:
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            return "missing"
        outcome = proposal.outcome()
        proposal.status = outcome
        if outcome == "passed":
            self._passed += 1
        return outcome

    def status(self) -> Dict[str, Any]:
        return {"proposals": len(self._proposals), "passed": self._passed,
                "voters": len(self._reputations)}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    council = WorkerCouncil()
    return {"status": "active", "module": "worker_council",
            **council.status()}
