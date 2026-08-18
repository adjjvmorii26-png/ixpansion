#!/usr/bin/env python3
"""1.2 Consensus EMA Reputation"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EMAReputation:
    alpha: float = 0.2
    scores: Dict[str, float] = field(default_factory=dict)
    events: Dict[str, int] = field(default_factory=dict)

    def observe(self, node_id: str, success: bool) -> float:
        prev = self.scores.get(node_id, 0.5)
        x = 1.0 if success else 0.0
        new = self.alpha * x + (1 - self.alpha) * prev
        self.scores[node_id] = new
        self.events[node_id] = self.events.get(node_id, 0) + 1
        return new

    def get(self, node_id: str) -> float:
        return self.scores.get(node_id, 0.5)

    def merge_peer(self, peer_scores: Dict[str, float], weight: float = 0.3) -> None:
        for nid, pscore in peer_scores.items():
            local = self.scores.get(nid, 0.5)
            self.scores[nid] = (1 - weight) * local + weight * pscore

    def ranked(self) -> List[tuple]:
        return sorted(self.scores.items(), key=lambda x: -x[1])

    def snapshot(self) -> dict:
        return {"nodes": len(self.scores), "top": self.ranked()[:5], "alpha": self.alpha}
