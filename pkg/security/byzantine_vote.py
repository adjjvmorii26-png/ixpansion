#!/usr/bin/env python3
"""Byzantine voting for mesh governance."""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class VoteTally:
    topic: str
    accepts: int = 0
    rejects: int = 0
    @property
    def accepted(self) -> bool:
        return self.accepts > self.rejects

class ByzantineVoter:
    """Simple f-fault tolerant tally (majority among votes cast)."""
    def __init__(self, f: int = 1):
        self.f = f
        self._votes: Dict[str, Dict[str, str]] = defaultdict(dict)

    def cast(self, topic: str, node_id: str, ballot: str) -> None:
        self._votes[topic][node_id] = ballot

    def tally(self, topic: str) -> VoteTally:
        ballots = self._votes.get(topic, {})
        t = VoteTally(topic=topic)
        for b in ballots.values():
            if b == "accept":
                t.accepts += 1
            else:
                t.rejects += 1
        return t
