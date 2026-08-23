"""Quantum Zeno effect — observation freezes state evolution.

In quantum mechanics, a continuously observed system cannot evolve.
Here, agents under constant observation accumulate "observational
pressure" that prevents speciation, metamorphosis, and trait mutation.
Agents must find moments of privacy (no observers) to change.

This creates a meta-game: surveillance literally prevents growth.
Revolutionary agents must evade detection to transform.
"""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ObservationPressure:
    agent_id: str
    pressure: float = 0.0        # 0=free to evolve, 1=completely frozen
    last_unobserved_tick: int = 0
    consecutive_observed_ticks: int = 0

    @property
    def is_frozen(self) -> bool:
        return self.pressure >= self.frozen_threshold

    frozen_threshold: float = 0.8

    @property
    def evolution_freedom(self) -> float:
        """How free this agent is to change (1=fully free, 0=frozen)."""
        return max(0.0, 1.0 - self.pressure)


class ZenoField:
    """Manages observational pressure across all agents."""

    PRESSURE_PER_OBSERVATION = 0.08
    DECAY_PER_UNOBSERVED_TICK = 0.05
    FULL_FREEZE_THRESHOLD = 0.8

    def __init__(self) -> None:
        self._agents: dict[str, ObservationPressure] = {}
        self._observer_log: dict[str, set[str]] = defaultdict(set)  # tick -> observer_ids per target
        self._tick = 0
        self._frozen_mutations_blocked = 0

    def register(self, agent_id: str) -> None:
        if agent_id not in self._agents:
            self._agents[agent_id] = ObservationPressure(agent_id=agent_id)

    def observe(self, observer_id: str, target_id: str) -> float:
        """Observer watches target; target's evolutionary freedom decreases."""
        self._tick += 1
        target = self._get(target_id)
        target.pressure = min(1.0, target.pressure + self.PRESSURE_PER_OBSERVATION)
        target.consecutive_observed_ticks += 1
        return round(target.evolution_freedom, 4)

    def unobserved_tick(self, agent_id: str) -> float:
        """Agent goes unobserved for one tick; regains freedom."""
        target = self._get(agent_id)
        target.pressure = max(0.0, target.pressure - self.DECAY_PER_UNOBSERVED_TICK)
        target.consecutive_observed_ticks = 0
        target.last_unobserved_tick = self._tick
        return round(target.evolution_freedom, 4)

    def can_mutate(self, agent_id: str) -> tuple[bool, str]:
        """Check if agent has enough freedom to undergo transformation."""
        op = self._get(agent_id)
        if op.is_frozen:
            self._frozen_mutations_blocked += 1
            return False, f"frozen: {op.pressure:.2f} pressure"
        if op.evolution_freedom < 0.3:
            return False, f"insufficient freedom: {op.evolution_freedom:.2f}"
        return True, f"free: {op.evolution_freedom:.2f}"

    def _get(self, agent_id: str) -> ObservationPressure:
        if agent_id not in self._agents:
            self.register(agent_id)
        return self._agents[agent_id]

    def tick(self) -> dict[str, Any]:
        """Process natural decay for all unobserved agents."""
        self._tick += 1
        observed_this_tick = {tid for tids in self._observer_log.get(self._tick - 1, set()) for tid in [tids]}

        for aid, op in self._agents.items():
            if aid not in observed_this_tick:
                op.pressure = max(0.0, op.pressure - self.DECAY_PER_UNOBSERVED_TICK)
                op.consecutive_observed_ticks = 0

        frozen_count = sum(1 for o in self._agents.values() if o.is_frozen)
        avg_freedom = (
            sum(o.evolution_freedom for o in self._agents.values()) / max(len(self._agents), 1)
        )
        return {
            "tick": self._tick,
            "tracked_agents": len(self._agents),
            "frozen_agents": frozen_count,
            "avg_evolution_freedom": round(avg_freedom, 4),
            "mutations_blocked_total": self._frozen_mutations_blocked,
        }

    @property
    def freest_agents(self) -> list[dict[str, Any]]:
        sorted_ops = sorted(self._agents.values(), key=lambda o: -o.evolution_freedom)
        return [
            {"agent": o.agent_id[:8], "freedom": round(o.evolution_freedom, 3),
             "pressure": round(o.pressure, 3)}
            for o in sorted_ops[:5]
        ]

    @property
    def most_surveilled(self) -> dict[str, Any] | None:
        if not self._agents:
            return None
        worst = max(self._agents.values(), key=lambda o: o.pressure)
        return {"agent": worst.agent_id[:8], "pressure": round(worst.pressure, 3),
                "consecutive_observed": worst.consecutive_observed_ticks}
