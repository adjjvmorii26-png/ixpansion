"""Ritual formation engine — group behaviors become sacred patterns.

When multiple agents perform the same action sequence in the same order,
a "ritual" begins to form. Each correct participation strengthens it;
deviation or absence weakens it. Fully-formed rituals (high potency)
grant passive bonuses to all participants.

Rituals are the engine's version of culture: they emerge from behavior,
persist beyond individual agents, and constrain future behavior.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class RitualState(Enum):
    SEEDLING = auto()      # Just noticed; fragile
    FORMING = auto()       # Multiple participants; gaining structure
    ESTABLISHED = auto()   # Stable; grants bonuses
    SACRED = auto()        # Maximum power; deviation is catastrophic
    FORGOTTEN = auto()     # Decayed below viability


@dataclass
class Ritual:
    ritual_id: str
    sequence: list[str]            # Ordered actions that define this ritual
    potency: float = 0.1           # 0-1; how powerful/established
    participants: set[str] = field(default_factory=set)
    correct_performances: int = 0
    deviations: int = 0

    @property
    def state(self) -> RitualState:
        if self.potency <= 0.05:
            return RitualState.FORGOTTEN
        elif self.potency >= 0.9 and len(self.participants) >= 5:
            return RitualState.SACRED
        elif self.potency >= 0.6:
            return RitualState.ESTABLISHED
        elif self.potency >= 0.25:
            return RitualState.FORMING
        return RitualState.SEEDLING

    @property
    def bonus_multiplier(self) -> float:
        """Bonus granted to participants when ritual is performed."""
        state = self.state
        if state == RitualState.SACRED:
            return 2.0
        elif state == RitualState.ESTABLISHED:
            return 1.5
        elif state == RitualState.FORMING:
            return 1.2
        return 1.0


class RitualEngine:
    MIN_PARTICIPANTS = 2
    MIN_SEQUENCE_LENGTH = 3
    DECAY_PER_TICK = 0.01

    def __init__(self) -> None:
        self._rituals: dict[str, Ritual] = {}
        self._action_sequences: dict[str, list[str]] = defaultdict(list)  # agent_id -> recent actions
        self._tick = 0

    def record_action(self, agent_id: str, action: str) -> None:
        """Track agent's action history for pattern detection."""
        seq = self._action_sequences[agent_id]
        seq.append(action)
        if len(seq) > 20:
            self._action_sequences[agent_id] = seq[-20:]

        # Check if this completes a known ritual sequence
        for ritual in self._rituals.values():
            if self._matches_ritual(seq, ritual):
                self._perform(ritual, agent_id)
                return

        # Check for new ritual formation (same sequence from multiple agents)
        self._detect_new_pattern(agent_id)

    def _matches_ritual(self, recent_actions: list[str], ritual: Ritual) -> bool:
        """Check if the tail of recent_actions matches the ritual sequence."""
        seq_len = len(ritual.sequence)
        if len(recent_actions) < seq_len:
            return False
        return recent_actions[-seq_len:] == ritual.sequence

    def _perform(self, ritual: Ritual, agent_id: str) -> None:
        """Correct performance of a ritual."""
        ritual.correct_performances += 1
        ritual.participants.add(agent_id)
        ritual.potency = min(1.0, ritual.potency + 0.08)

    def _deviate(self, ritual: Ritual) -> None:
        """Someone broke the sequence."""
        ritual.deviations += 1
        penalty = 0.15 if ritual.state == RitualState.SACRED else 0.05
        ritual.potency = max(0.0, ritual.potency - penalty)

    def _detect_new_pattern(self, new_agent_id: str) -> None:
        """Check if multiple agents are performing similar sequences."""
        # Get the last 3+ actions from each agent
        sequences_by_agent = {}
        for aid, actions in self._action_sequences.items():
            if len(actions) >= self.MIN_SEQUENCE_LENGTH:
                tail = tuple(actions[-self.MIN_SEQUENCE_LENGTH:])
                sequences_by_agent.setdefault(tail, set()).add(aid)

        for seq_tuple, agents in sequences_by_agent.items():
            if len(agents) >= self.MIN_PARTICIPANTS and list(seq_tuple) not in [
                r.sequence for r in self._rituals.values()
            ]:
                rid = hashlib.sha256(f"{seq_tuple}".encode()).hexdigest()[:10]
                ritual = Ritual(
                    ritual_id=rid,
                    sequence=list(seq_tuple),
                    participants=set(agents),
                    potency=len(agents) * 0.1,
                )
                self._rituals[rid] = ritual

    def tick(self) -> dict[str, Any]:
        """Natural decay of rituals without participation."""
        self._tick += 1
        forgotten = []
        for rid, ritual in self._rituals.items():
            ritual.potency -= self.DECAY_PER_TICK
            if ritual.potency <= 0:
                forgotten.append(rid)

        for rid in forgotten:
            del self._rituals[rid]

        states = Counter(r.state.name for r in self._rituals.values())
        return {
            "active_rituals": len(self._rituals),
            "state_distribution": dict(states),
            "forgotten_this_tick": len(forgotten),
        }

    @property
    def sacred_rituals(self) -> list[dict[str, Any]]:
        return [
            {"sequence": r.sequence, "participants": len(r.participants),
             "potency": round(r.potency, 3), "bonus": r.bonus_multiplier}
            for r in self._rituals.values() if r.state == RitualState.SACRED
        ]

    @property
    def stats(self) -> dict[str, Any]:
        total_participants = sum(len(r.participants) for r in self._rituals.values())
        avg_potency = sum(r.potency for r in self._rituals.values()) / max(len(self._rituals), 1)
        return {
            "total_rituals": len(self._rituals),
            "avg_potency": round(avg_potency, 4),
            "total_unique_participants": total_participants,
            "tracked_agents": len(self._action_sequences),
        }
