#!/usr/bin/env python3
"""Mycelial Governor — organic growth regulation layer.

Prevents runaway expansion by applying biological constraints:
- Nutrient scarcity: growth requires available nutrients
- Signal decay: signals weaken over distance and time
- Hyphal arbitration: competing growth proposals are negotiated

The governor doesn't block growth — it channels it. Like mycelium
in a forest, it ensures resources are distributed sustainably
and no single organism dominates.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class NutrientPool:
    pool_id: str
    total: float = 100.0
    available: float = 100.0
    reserved: float = 0.0
    regeneration_rate: float = 0.5

    def regenerate(self) -> None:
        self.available = min(self.total, self.available + self.regeneration_rate)

    def allocate(self, amount: float) -> float:
        granted = min(amount, self.available)
        self.available -= granted
        self.reserved += granted
        return granted

    def release(self, amount: float) -> None:
        self.reserved = max(0.0, self.reserved - amount)
        self.available = min(self.total, self.available + amount)

    @property
    def scarcity(self) -> float:
        return max(0.0, 1.0 - self.available / max(0.01, self.total))


@dataclass
class GrowthProposal:
    proposal_id: str
    organism_id: str
    requested_nutrients: float
    signal_strength: float
    signal_decay: float = 0.1
    position: tuple[float, float] = (0.0, 0.0)
    approved: bool = False
    granted: float = 0.0
    reason: str = ""


@dataclass
class Organism:
    organism_id: str
    species: str
    energy: float = 1.0
    growth_rate: float = 0.1
    signal_strength: float = 0.5
    proposals_made: int = 0
    proposals_approved: int = 0

    @property
    def efficiency(self) -> float:
        if self.proposals_made == 0:
            return 0.5
        return self.proposals_approved / self.proposals_made


@dataclass
class MycelialGovernor:
    """Organic growth regulation through resource management."""
    max_signal_distance: float = 20.0
    signal_decay_rate: float = 0.1
    arbitration_radius: float = 10.0
    scarcity_threshold: float = 0.7
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = __import__("random").Random(self.seed)
        self._pool = NutrientPool(pool_id="main")
        self._organisms: dict[str, Organism] = {}
        self._proposals: list[GrowthProposal] = []
        self._arbiter_log: list[dict[str, Any]] = []
        self._tick = 0

    def add_organism(self, org_id: str, species: str,
                     position: tuple[float, float] | None = None) -> Organism:
        org = Organism(organism_id=org_id, species=species)
        self._organisms[org_id] = org
        return org

    def propose_growth(self, org_id: str, nutrients: float,
                       position: tuple[float, float] | None = None) -> GrowthProposal:
        org = self._organisms[org_id]
        position = position or (self._rng.uniform(0, 50), self._rng.uniform(0, 50))
        pid = hashlib.sha256(f"{org_id}:{self._tick}".encode()).hexdigest()[:12]

        # Signal decay based on distance from pool center
        distance = math.dist(position, (25, 25))
        decay = math.exp(-self.signal_decay_rate * distance / self.max_signal_distance)
        signal = org.signal_strength * decay

        proposal = GrowthProposal(
            proposal_id=pid,
            organism_id=org_id,
            requested_nutrients=nutrients,
            signal_strength=round(signal, 4),
            signal_decay=round(decay, 4),
            position=position,
        )
        org.proposals_made += 1
        self._proposals.append(proposal)
        return proposal

    def arbitrate(self, proposal: GrowthProposal) -> GrowthProposal:
        """Evaluate a growth proposal against constraints."""
        # Check nutrient availability
        if self._pool.scarcity > self.scarcity_threshold:
            proposal.approved = False
            proposal.reason = f"scarcity_level_{self._pool.scarcity:.2f}"
            return proposal

        # Check signal strength
        if proposal.signal_strength < 0.1:
            proposal.approved = False
            proposal.reason = "signal_too_weak"
            return proposal

        # Check competing proposals (arbitration)
        nearby = [
            p for p in self._proposals
            if p.proposal_id != proposal.proposal_id
            and p.approved is False and p.reason == ""
            and math.dist(p.position, proposal.position) < self.arbitration_radius
        ]

        if nearby:
            # Prioritize by signal strength
            all_proposals = [proposal] + nearby
            all_proposals.sort(key=lambda p: -p.signal_strength)
            winner = all_proposals[0]
            for p in all_proposals[1:]:
                p.approved = False
                p.reason = "outcompeted_in_arbitration"
            if winner.proposal_id == proposal.proposal_id:
                granted = self._pool.allocate(proposal.requested_nutrients)
                proposal.approved = True
                proposal.granted = granted
                proposal.reason = "arbitration_won"
                self._organisms[proposal.organism_id].proposals_approved += 1
                self._arbiter_log.append({
                    "tick": self._tick, "winner": proposal.organism_id,
                    "losers": len(nearby), "granted": round(granted, 3),
                })
            else:
                proposal.approved = False
                proposal.reason = "outcompeted_in_arbitration"
        else:
            # No competition — allocate
            granted = self._pool.allocate(proposal.requested_nutrients)
            proposal.approved = True
            proposal.granted = granted
            proposal.reason = "no_competition"
            self._organisms[proposal.organism_id].proposals_approved += 1

        return proposal

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        self._pool.regenerate()

        # Each organism proposes growth
        new_proposals = 0
        for org in self._organisms.values():
            nutrients = self._rng.uniform(0.5, 3.0)
            proposal = self.propose_growth(org.organism_id, nutrients)
            self.arbitrate(proposal)
            new_proposals += 1

        return {"tick": self._tick, "new_proposals": new_proposals}

    def governor_report(self) -> dict[str, Any]:
        approved = sum(1 for p in self._proposals if p.approved)
        return {
            "tick": self._tick,
            "nutrient_pool": {
                "available": round(self._pool.available, 2),
                "reserved": round(self._pool.reserved, 2),
                "scarcity": round(self._pool.scarcity, 3),
            },
            "total_proposals": len(self._proposals),
            "approved": approved,
            "approval_rate": round(approved / max(1, len(self._proposals)), 3),
            "organisms": {
                oid: {"efficiency": round(o.efficiency, 3), "proposals": o.proposals_made}
                for oid, o in self._organisms.items()
            },
        }


def demo() -> dict[str, Any]:
    gov = MycelialGovernor(seed=42)
    species = ["alpha", "beta", "gamma"]
    for i in range(8):
        gov.add_organism(f"org-{i}", species[i % 3])

    for _ in range(15):
        gov.tick()

    return gov.governor_report()


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
