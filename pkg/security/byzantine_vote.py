#!/usr/bin/env python3
"""Distributed Byzantine Consensus Vote (1.3 trust scope)"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Ballot:
    voter_id: str
    proposal_id: str
    choice: str
    weight: float = 1.0


@dataclass
class VoteResult:
    proposal_id: str
    accepted: bool
    tally: Dict[str, float]
    participating: int
    threshold: float
    byzantine_tolerance_f: int


class ByzantineVoter:
    def __init__(self, f: int = 1):
        self.f = f
        self.min_nodes = 3 * f + 1
        self.ballots: Dict[str, List[Ballot]] = {}
        self.results: List[VoteResult] = []

    def cast(self, proposal_id: str, voter_id: str, choice: str, weight: float = 1.0) -> None:
        choice = choice if choice in ("accept", "reject", "abstain") else "abstain"
        self.ballots.setdefault(proposal_id, []).append(
            Ballot(voter_id=voter_id, proposal_id=proposal_id, choice=choice, weight=weight)
        )

    def tally(self, proposal_id: str) -> VoteResult:
        votes = self.ballots.get(proposal_id, [])
        latest: Dict[str, Ballot] = {}
        for b in votes:
            latest[b.voter_id] = b
        tally: Dict[str, float] = {"accept": 0.0, "reject": 0.0, "abstain": 0.0}
        for b in latest.values():
            tally[b.choice] += b.weight
        participating = len(latest)
        active = tally["accept"] + tally["reject"]
        threshold = max(self.f + 1, (active / 2) + 0.01) if active else float("inf")
        accepted = (
            participating >= (2 * self.f + 1)
            and tally["accept"] > tally["reject"]
            and tally["accept"] >= (self.f + 1)
        )
        result = VoteResult(
            proposal_id=proposal_id, accepted=accepted, tally=tally,
            participating=participating, threshold=threshold, byzantine_tolerance_f=self.f,
        )
        self.results.append(result)
        return result

    def snapshot(self) -> dict:
        return {"f": self.f, "min_nodes": self.min_nodes, "proposals": len(self.ballots), "results": len(self.results)}
