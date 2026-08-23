"""Emergent hierarchy — self-organizing social structures.

Agents don't have assigned ranks. Instead, a dominance hierarchy
emerges naturally from interaction patterns: when agent A consistently
yields to agent B, B's authority score rises. Over time, a stable
pecking order forms. Coalitions form between agents of similar rank.
Leaders emerge at the top; outcasts sink to the bottom.

Power here is purely informational — it shapes behavior, not physics.
"""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class SocialRank(Enum):
    SOVEREIGN = auto()   # Top ~5%
    COUNCIL = auto()     # Next ~15%
    MEMBER = auto()      # Middle ~50%
    MARGINAL = auto()    # Lower ~20%
    OUTCAST = auto()     # Bottom ~10%


@dataclass
class AgentNode:
    agent_id: str
    species: str
    authority: float = 0.5      # 0=powerless, 1=absolute authority
    deference_paid: float = 0.0  # Total submission shown to others
    deference_received: float = 0.0
    coalition: str | None = None

    @property
    def net_influence(self) -> float:
        return self.deference_received - self.deference_paid

    @property
    def rank(self) -> SocialRank:
        if self.authority >= 0.85:
            return SocialRank.SOVEREIGN
        elif self.authority >= 0.65:
            return SocialRank.COUNCIL
        elif self.authority >= 0.35:
            return SocialRank.MEMBER
        elif self.authority >= 0.15:
            return SocialRank.MARGINAL
        return SocialRank.OUTCAST


@dataclass
class Coalition:
    name: str
    members: set[str] = field(default_factory=set)
    cohesion: float = 0.5

    @property
    def combined_authority(self) -> float:
        return min(1.0, len(self.members) * 0.1)


class EmergentHierarchy:
    AUTHORITY_LEARNING_RATE = 0.05
    COALITION_SIMILARITY_THRESHOLD = 0.2

    def __init__(self) -> None:
        self._agents: dict[str, AgentNode] = {}
        self._coalitions: dict[str, Coalition] = {}
        self._interaction_log: list[dict[str, Any]] = []

    def join(self, agent_id: str, species: str) -> None:
        if agent_id not in self._agents:
            self._agents[agent_id] = AgentNode(agent_id=agent_id, species=species)

    def interact(self, dominant_id: str, submissive_id: str) -> dict[str, Any]:
        """Record a dominance/submission interaction."""
        dom = self._agents.get(dominant_id)
        sub = self._agents.get(submissive_id)
        if not dom or not sub:
            return {"error": "unknown_agent"}

        # Submissive agent's authority decreases slightly
        sub.authority = max(0.0, sub.authority - self.AUTHORITY_LEARNING_RATE)
        sub.deference_paid += 1

        # Dominant agent's authority increases slightly
        dom.authority = min(1.0, dom.authority + self.AUTHORITY_LEARNING_RATE * 0.8)
        dom.deference_received += 1

        self._check_coalition_formation(dom, sub)

        record = {
            "dominant": dominant_id, "submissive": submissive_id,
            "dom_authority": round(dom.authority, 4),
            "sub_authority": round(sub.authority, 4),
            "dom_rank": dom.rank.name,
            "sub_rank": sub.rank.name,
        }
        self._interaction_log.append(record)
        return record

    def _check_coalition_formation(self, a: AgentNode, b: AgentNode) -> None:
        """Agents with similar authority and same species may ally."""
        if abs(a.authority - b.authority) > self.COALITION_SIMILARITY_THRESHOLD:
            return
        if a.species != b.species:
            return
        if a.coalition and a.coalition == b.coalition:
            return  # Already allied

        # Form new coalition or merge into existing
        if a.coalition and b.coalition is None:
            self._coalitions[a.coalition].members.add(b.agent_id)
            b.coalition = a.coalition
        elif b.coalition and a.coalition is None:
            self._coalitions[b.coalition].members.add(a.agent_id)
            a.coalition = b.coalition
        elif a.coalition is None and b.coalition is None:
            cname = f"pact_{a.species}_{len(self._coalitions)}"
            coalition = Coalition(name=cname, members={a.agent_id, b.agent_id})
            self._coalitions[cname] = coalition
            a.coalition = cname
            b.coalition = cname

    def challenge(self, challenger_id: str, target_id: str) -> dict[str, Any]:
        """Directly contest authority. Winner takes from loser."""
        challenger = self._agents.get(challenger_id)
        target = self._agents.get(target_id)
        if not challenger or not target:
            return {"error": "unknown_agent"}

        # Higher authority usually wins
        total = challenger.authority + target.authority
        roll = challenger.authority / max(total, 0.01)

        import random
        rng = random.Random()
        success = rng.random() < roll

        transfer = 0.05
        if success:
            challenger.authority = min(1.0, challenger.authority + transfer)
            target.authority = max(0.0, target.authority - transfer)
        else:
            challenger.authority = max(0.0, challenger.authority - transfer * 1.5)
            target.authority = min(1.0, target.authority + transfer * 0.5)

        return {
            "challenger": challenger_id, "target": target_id,
            "success": success,
            "new_challenger_rank": challenger.rank.name,
            "new_target_rank": target.rank.name,
        }

    @property
    def hierarchy_tree(self) -> list[dict[str, Any]]:
        sorted_agents = sorted(self._agents.values(), key=lambda a: -a.authority)
        tree = []
        for node in sorted_agents:
            entry = {
                "id": node.agent_id,
                "species": node.species,
                "authority": round(node.authority, 3),
                "rank": node.rank.name,
                "coalition": node.coalition,
                "net_influence": round(node.net_influence, 1),
            }
            tree.append(entry)
        return tree

    @property
    def sovereigns(self) -> list[str]:
        return [a.agent_id for a in self._agents.values() if a.rank == SocialRank.SOVEREIGN]

    @property
    def stats(self) -> dict[str, Any]:
        rank_dist = defaultdict(int)
        for a in self._agents.values():
            rank_dist[a.rank.name] += 1
        avg_auth = sum(a.authority for a in self._agents.values()) / max(len(self._agents), 1)
        return {
            "population": len(self._agents),
            "rank_distribution": dict(rank_dist),
            "avg_authority": round(avg_auth, 4),
            "coalitions": {name: len(c.members) for name, c in self._coalitions.items()},
            "total_interactions": len(self._interaction_log),
        }
