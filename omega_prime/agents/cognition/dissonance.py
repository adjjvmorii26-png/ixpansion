"""Cognitive dissonance engine.

When an agent's inference engine produces contradictory conclusions
from the same stimulus, cognitive pressure accumulates. Low pressure
causes subtle behavioral drift. Medium pressure causes erratic decisions.
High pressure triggers an identity crisis: the agent temporarily loses
its rank, coalition membership, and species-specific abilities until
the contradiction resolves.

Resolution happens through evidence gathering, social influence from
trusted peers, or spontaneous belief mutation.
"""
from __future__ import annotations

import hashlib
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class PressureLevel(Enum):
    HARMONIOUS = auto()    # No contradictions
    TENSION = auto()       # Minor contradictions; slight drift
    STRAIN = auto()        # Noticeable; erratic decisions
    FRACTURE = auto()      # Identity crisis imminent
    CRISIS = auto()        # Full breakdown; abilities suspended


@dataclass
class Belief:
    """A single proposition the agent holds to be true."""

    belief_id: str
    statement: str
    confidence: float          # 0-1
    source: str                # Where this belief came from
    tick_formed: int
    contradicts: set[str] = field(default_factory=set)  # Other belief_ids this conflicts with

    @property
    def is_confident(self) -> bool:
        return self.confidence >= 0.7


@dataclass
class DissonanceEvent:
    agent_id: str
    belief_a_id: str
    belief_b_id: str
    pressure_generated: float
    resolved_at_tick: int | None = None
    resolution_method: str | None = None


class CognitiveDissonanceEngine:
    PRESSURE_PER_CONTRADICTION = 0.15
    CRISIS_THRESHOLD = 0.85
    RESOLUTION_DECAY = 0.03

    def __init__(self) -> None:
        self._beliefs: dict[str, list[Belief]] = defaultdict(list)  # agent_id -> beliefs
        self._pressure: dict[str, float] = defaultdict(float)
        self._events: list[DissonanceEvent] = []
        self._in_crisis: set[str] = set()
        self._tick = 0

    def form_belief(self, agent_id: str, statement: str,
                    confidence: float, source: str,
                    contradicts: list[str] | None = None) -> Belief:
        """Agent forms a new belief. If it contradicts existing beliefs, pressure rises."""
        self._tick += 1
        bid = hashlib.sha256(f"{agent_id}:{statement}:{self._tick}".encode()).hexdigest()[:10]
        belief = Belief(
            belief_id=bid, statement=statement,
            confidence=max(0.0, min(1.0, confidence)),
            source=source, tick_formed=self._tick,
            contradicts=set(contradicts or []),
        )
        self._beliefs[agent_id].append(belief)

        # Check for contradictions with existing beliefs
        new_contradictions = 0
        for existing in self._beliefs[agent_id]:
            if existing.belief_id == bid:
                continue
            if bid in existing.contradicts or existing.belief_id in (contradicts or []):
                new_contradictions += 1

        if new_contradictions > 0:
            pressure_gain = new_contradictions * self.PRESSURE_PER_CONTRADICTION
            self._pressure[agent_id] += pressure_gain

            event = DissonanceEvent(
                agent_id=agent_id,
                belief_a_id=bid,
                belief_b_id="multiple" if new_contradictions > 1 else "",
                pressure_generated=pressure_gain,
            )
            self._events.append(event)

        return belief

    def tick(self) -> dict[str, Any]:
        """Process dissonance for all agents."""
        self._tick += 1
        crises_triggered = []
        resolutions = []

        for agent_id in list(self._pressure.keys()):
            level = self.get_pressure_level(agent_id)

            if level == PressureLevel.CRISIS and agent_id not in self._in_crisis:
                self._in_crisis.add(agent_id)
                crises_triggered.append(agent_id)

            elif agent_id in self._in_crisis and level != PressureLevel.CRISIS:
                self._in_crisis.discard(agent_id)
                resolutions.append(agent_id)

            # Natural decay toward zero if no active contradictions
            if not self._has_active_contradictions(agent_id):
                self._pressure[agent_id] = max(0.0,
                    self._pressure[agent_id] - self.RESOLUTION_DECAY)

        return {
            "tick": self._tick,
            "crises_triggered": crises_triggered,
            "crises_resolved": resolutions,
            "agents_in_crisis": list(self._in_crisis),
        }

    def resolve_belief(self, agent_id: str, discard_belief_id: str) -> float:
        """Agent consciously abandons a belief; pressure drops proportionally."""
        beliefs = self._beliefs.get(agent_id, [])
        target = next((b for b in beliefs if b.belief_id == discard_belief_id), None)
        if not target:
            return 0.0

        relief = target.confidence * self.PRESSURE_PER_CONTRADICTION * 2
        self._pressure[agent_id] = max(0.0, self._pressure[agent_id] - relief)
        self._beliefs[agent_id] = [b for b in beliefs if b.belief_id != discard_belief_id]

        for event in self._events:
            if event.agent_id == agent_id and event.resolution_method is None:
                event.resolution_method = f"discarded:{discard_belief_id[:8]}"
                event.resolved_at_tick = self._tick
        return round(relief, 4)

    def _has_active_contradictions(self, agent_id: str) -> bool:
        beliefs = self._beliefs.get(agent_id, [])
        for b in beliefs:
            if any(b.contradicts & {o.belief_id for o in beliefs} for o in beliefs):
                return True
            if any(b.belief_id in o.contradicts for o in beliefs):
                return True
        return False

    def get_pressure_level(self, agent_id: str) -> PressureLevel:
        p = self._pressure.get(agent_id, 0.0)
        if p >= self.CRISIS_THRESHOLD:
            return PressureLevel.CRISIS
        elif p >= 0.6:
            return PressureLevel.FRACTURE
        elif p >= 0.35:
            return PressureLevel.STRAIN
        elif p >= 0.1:
            return PressureLevel.TENSION
        return PressureLevel.HARMONIOUS

    @property
    def stats(self) -> dict[str, Any]:
        levels = defaultdict(int)
        for aid in self._pressure:
            levels[self.get_pressure_level(aid).name] += 1
        return {
            "tracked_agents": len(self._pressure),
            "total_beliefs": sum(len(v) for v in self._beliefs.values()),
            "dissonance_events": len(self._events),
            "agents_in_crisis": len(self._in_crisis),
            "level_distribution": dict(levels),
        }
