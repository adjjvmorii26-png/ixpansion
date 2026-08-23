"""Time crystal oscillator.

A discrete-time crystal is a structure that periodically returns to
its initial state after N pulses. Agents within its influence radius
experience "echoes" — fragments of their own past states from previous
oscillation cycles. This creates temporal recursion: agents can
effectively remember their own future by recalling what they did last cycle.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CrystalState:
    """A snapshot of an agent's state at one point in the oscillation."""

    tick: int
    agent_id: str
    position: tuple[float, float]
    action: str
    entropy_level: float

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "tick": self.tick,
            "position": list(self.position),
            "action": self.action,
            "entropy": round(self.entropy_level, 4),
        }


@dataclass
class TimeCrystal:
    """A localized temporal oscillator with a fixed period."""

    crystal_id: str
    center: tuple[float, float]
    radius: float
    period: int          # Number of ticks per full oscillation
    phase: int = 0       # Current position in the cycle

    @property
    def normalized_phase(self) -> float:
        return self.phase / max(self.period, 1)

    def advance(self) -> bool:
        """Advance one tick. Returns True if a full cycle completed."""
        self.phase = (self.phase + 1) % self.period
        return self.phase == 0

    def contains(self, pos: tuple[float, float]) -> bool:
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        return (dx ** 2 + dy ** 2) <= (self.radius ** 2)


class TimeCrystalLattice:
    def __init__(self) -> None:
        self._crystals: dict[str, TimeCrystal] = {}
        self._agent_history: dict[str, list[CrystalState]] = defaultdict(list)
        self._tick = 0
        self._echo_log: list[dict[str, Any]] = []

    def create(self, center: tuple[float, float], radius: float, period: int) -> str:
        cid = hashlib.sha256(f"{center}:{period}:{self._tick}".encode()).hexdigest()[:12]
        crystal = TimeCrystal(crystal_id=cid, center=center, radius=radius, period=period)
        self._crystals[cid] = crystal
        return cid

    def record_agent_state(self, agent_id: str, position: tuple[float, float],
                           action: str, entropy: float) -> None:
        """Record what an agent did this tick for echo purposes."""
        state = CrystalState(
            tick=self._tick, agent_id=agent_id,
            position=position, action=action, entropy_level=entropy,
        )
        self._agent_history[agent_id].append(state)
        # Keep bounded history
        if len(self._agent_history[agent_id]) > 1000:
            self._agent_history[agent_id] = self._agent_history[agent_id][-500:]

    def tick(self) -> dict[str, Any]:
        """Advance all crystals. Generate echoes for agents inside influence."""
        self._tick += 1
        cycles_completed = []

        for crystal in self._crystals.values():
            completed = crystal.advance()
            if completed:
                cycles_completed.append(crystal.crystal_id)

        echoes = self._generate_echoes()
        return {
            "tick": self._tick,
            "cycles_completed": cycles_completed,
            "echoes_generated": len(echoes),
            "echoes": echoes[:5],
        }

    def _generate_echoes(self) -> list[dict[str, Any]]:
        """For each agent inside a crystal's influence, show them a past echo."""
        echoes = []
        for aid, history in self._agent_history.items():
            if not history or len(history) < 2:
                continue

            latest_pos = history[-1].position
            for crystal in self._crystals.values():
                if not crystal.contains(latest_pos):
                    continue

                # Find the state from exactly one period ago
                target_tick = self._tick - crystal.period
                past_state = next(
                    (s for s in reversed(history) if s.tick == target_tick), None
                )
                if not past_state:
                    continue

                # Echo fidelity decreases with distance from crystal center
                dx = latest_pos[0] - crystal.center[0]
                dy = latest_pos[1] - crystal.center[1]
                dist_ratio = ((dx ** 2 + dy ** 2) ** 0.5) / max(crystal.radius, 0.01)
                fidelity = max(0.0, 1.0 - dist_ratio)

                echo = {
                    "agent": aid,
                    "crystal": crystal.crystal_id,
                    "echoed_tick": past_state.tick,
                    "past_position": list(past_state.position),
                    "past_action": past_state.action,
                    "fidelity": round(fidelity, 4),
                    "message": f"You sense yourself at {list(past_state.position)} doing '{past_state.action}'...",
                }
                echoes.append(echo)
                self._echo_log.append(echo)

        return echoes

    def get_future_self(self, agent_id: str, periods_ahead: int = 1) -> dict[str, Any] | None:
        """Predict where the agent will be next period based on cyclical patterns."""
        history = self._agent_history.get(agent_id)
        if not history or len(history) < 2:
            return None

        # If agent is inside a crystal, predict periodic behavior
        latest = history[-1]
        for crystal in self._crystals.values():
            if crystal.contains(latest.position):
                lookback = crystal.period * periods_ahead
                idx = len(history) - 1 - lookback
                if idx >= 0:
                    predicted = history[idx]
                    return {
                        "predicted_position": list(predicted.position),
                        "predicted_action": predicted.action,
                        "confidence": round(1.0 / periods_ahead, 3),
                        "basis": f"temporal echo from {lookback} ticks ago",
                    }
        return None

    @property
    def active_crystals(self) -> list[dict[str, Any]]:
        return [
            {"id": c.crystal_id, "period": c.period, "phase": c.phase,
             "norm_phase": round(c.normalized_phase, 4), "radius": c.radius}
            for c in self._crystals.values()
        ]
