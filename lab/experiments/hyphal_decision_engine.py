#!/usr/bin/env python3
"""Hyphal Decision Engine — living network decision-making through consent.

Bridges hypha + consent + substrate + dream_compiler to model how a
mycelial network makes collective decisions. Each hypha proposes growth
into the substrate. The consent gate evaluates the proposal. Decisions
accumulate into a "consensus pulse" that determines the network's
collective action.

This is decentralized governance through biological metaphor —
no central authority, just consent-gated negotiation.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class HyphalTip:
    tip_id: str
    species: str
    position: tuple[float, float]
    energy: float = 1.0
    viability: float = 0.8
    proposals_made: int = 0
    proposals_approved: int = 0
    memory: list[dict[str, Any]] = field(default_factory=list)

    @property
    def influence(self) -> float:
        return self.viability * self.energy

    @property
    def trust_score(self) -> float:
        if self.proposals_made == 0:
            return 0.5
        return self.proposals_approved / self.proposals_made


@dataclass
class GrowthProposal:
    proposal_id: str
    tip_id: str
    target_site: str
    requested_nutrient: float
    offered_signal: float
    rationale: str


@dataclass
class ConsentDecision:
    proposal_id: str
    approved: bool
    reason: str
    granted_nutrient: float
    voters: list[str] = field(default_factory=list)


@dataclass
class HyphalDecisionEngine:
    """Decentralized decision-making through consent-gated negotiation."""
    minimum_signal: float = 0.15
    maximum_extraction: float = 0.35
    minimum_viability: float = 0.25
    quorum_size: int = 3
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._tips: dict[str, HyphalTip] = {}
        self._sites: dict[str, float] = {}  # site_id -> nutrient level
        self._proposals: list[GrowthProposal] = []
        self._decisions: list[ConsentDecision] = []
        self._consensus_log: list[dict[str, Any]] = []
        self._tick = 0

    def add_tip(self, tip_id: str, species: str,
                position: tuple[float, float] | None = None) -> HyphalTip:
        if position is None:
            position = (self._rng.uniform(0, 100), self._rng.uniform(0, 100))
        tip = HyphalTip(tip_id=tip_id, species=species, position=position)
        self._tips[tip_id] = tip
        return tip

    def add_site(self, site_id: str, nutrient: float = 10.0) -> None:
        self._sites[site_id] = nutrient

    def propose(self, tip_id: str, target_site: str,
                requested: float, signal: float) -> GrowthProposal:
        tip = self._tips[tip_id]
        tip.proposals_made += 1
        proposal = GrowthProposal(
            proposal_id=hashlib.sha256(
                f"{tip_id}:{target_site}:{self._tick}".encode()
            ).hexdigest()[:12],
            tip_id=tip_id,
            target_site=target_site,
            requested_nutrient=requested,
            offered_signal=signal,
            rationale=f"{tip.species} tip seeks {requested:.2f} from {target_site}",
        )
        self._proposals.append(proposal)
        return proposal

    def vote_on(self, proposal: GrowthProposal) -> ConsentDecision:
        """Other tips vote on the proposal."""
        voters: list[str] = []
        votes_for = 0
        votes_against = 0

        other_tips = [t for t in self._tips.values() if t.tip_id != proposal.tip_id]
        voter_pool = self._rng.sample(
            other_tips, min(self.quorum_size, len(other_tips))
        ) if other_tips else []

        for voter in voter_pool:
            voters.append(voter.tip_id)
            # Vote based on species affinity and proposal quality
            affinity = 1.0 if voter.species == self._tips[proposal.tip_id].species else 0.5
            quality = min(1.0, proposal.offered_signal / max(0.01, proposal.requested_nutrient))
            vote_score = affinity * quality * voter.influence

            if vote_score > 0.3:
                votes_for += 1
            else:
                votes_against += 1

        # Consent gate checks
        site_nutrient = self._sites.get(proposal.target_site, 0)
        tip = self._tips[proposal.tip_id]

        if tip.viability < self.minimum_viability:
            approved = False
            reason = "below_viability_threshold"
            granted = 0.0
        elif proposal.offered_signal < self.minimum_signal:
            approved = False
            reason = "insufficient_signal"
            granted = 0.0
        elif proposal.requested_nutrient > site_nutrient * self.maximum_extraction:
            approved = False
            reason = "exceeds_extraction_limit"
            granted = 0.0
        elif votes_for <= votes_against:
            approved = False
            reason = "rejected_by_quorum"
            granted = 0.0
        else:
            approved = True
            reason = "consensus_reached"
            granted = min(proposal.requested_nutrient, site_nutrient * self.maximum_extraction)
            self._sites[proposal.target_site] -= granted
            tip.proposals_approved += 1
            tip.energy = min(1.0, tip.energy + granted * 0.1)

        decision = ConsentDecision(
            proposal_id=proposal.proposal_id,
            approved=approved,
            reason=reason,
            granted_nutrient=round(granted, 4),
            voters=voters,
        )
        self._decisions.append(decision)
        tip.memory.append({
            "proposal": proposal.proposal_id,
            "approved": approved,
            "reason": reason,
        })

        return decision

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        # Each tip makes a proposal
        new_decisions = 0
        for tip in self._tips.values():
            if tip.energy <= 0:
                continue
            site_ids = list(self._sites.keys())
            if not site_ids:
                continue
            target = self._rng.choice(site_ids)
            requested = self._rng.uniform(0.1, 1.0)
            signal = self._rng.uniform(0.1, 0.8)
            proposal = self.propose(tip.tip_id, target, requested, signal)
            decision = self.vote_on(proposal)
            new_decisions += 1

        approved = sum(1 for d in self._decisions[-len(self._tips):] if d.approved)
        self._consensus_log.append({
            "tick": self._tick,
            "proposals": len(self._tips),
            "approved": approved,
        })

        return {"tick": self._tick, "new_decisions": new_decisions}

    def consensus_summary(self) -> dict[str, Any]:
        total = len(self._decisions)
        approved = sum(1 for d in self._decisions if d.approved)
        reasons = defaultdict(int)
        for d in self._decisions:
            reasons[d.reason] += 1

        tip_stats = {}
        for tid, tip in self._tips.items():
            tip_stats[tid] = {
                "proposals": tip.proposals_made,
                "approved": tip.proposals_approved,
                "trust": round(tip.trust_score, 3),
            }

        return {
            "total_proposals": total,
            "approved": approved,
            "approval_rate": round(approved / max(1, total), 3),
            "rejection_reasons": dict(reasons),
            "tip_stats": tip_stats,
            "site_nutrients": {k: round(v, 2) for k, v in self._sites.items()},
        }


def demo() -> dict[str, Any]:
    engine = HyphalDecisionEngine(seed=42)
    species = ["alpha", "beta", "gamma"]
    for i in range(8):
        engine.add_tip(f"tip-{i}", species[i % 3])
    for i in range(4):
        engine.add_site(f"site-{i}", nutrient=5.0 + i * 2)

    for _ in range(10):
        engine.tick()

    return engine.consensus_summary()


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
