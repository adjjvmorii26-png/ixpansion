"""Ghost protocol.

When an agent's entropy budget is fully depleted, it doesn't "die" —
it becomes a ghost. Ghosts exist in a superposition of presence:
they can observe all realm events with perfect clarity (no perception
cost) but cannot take any physical action. Ghosts passively accumulate
knowledge and can emit weak "whispers" into the morphic field.

Ghosts recover by passively regenerating entropy. Once above the
resurrection threshold, they return to corporeal form with their
ghost-era knowledge intact.
"""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GhostRecord:
    agent_id: str
    species: str
    entered_ghost_at: float = field(default_factory=time.monotonic)
    observations: list[dict[str, Any]] = field(default_factory=list)
    whispers_sent: int = 0

    @property
    def ghost_age_s(self) -> float:
        return round(time.monotonic() - self.entered_ghost_at, 2)


class GhostProtocol:
    RESURRECTION_THRESHOLD = 0.15  # Fraction of capacity needed to return
    WHISPER_STRENGTH = 0.1        # Weak signal compared to active agents

    def __init__(self) -> None:
        self._ghosts: dict[str, GhostRecord] = {}
        self._whisper_buffer: list[dict[str, Any]] = []

    def enter_ghost_state(self, agent_id: str, species: str) -> GhostRecord:
        record = GhostRecord(agent_id=agent_id, species=species)
        self._ghosts[agent_id] = record
        return record

    def exit_ghost_state(self, agent_id: str) -> dict[str, Any] | None:
        """Return an agent to corporeal form with accumulated ghost knowledge."""
        record = self._ghosts.pop(agent_id, None)
        if not record:
            return None
        return {
            "agent": agent_id,
            "species": record.species,
            "ghost_duration_s": record.ghost_age_s,
            "observations_collected": len(record.observations),
            "whispers_sent": record.whispers_sent,
            "bonus_knowledge": [o.get("insight") for o in record.observations if o.get("insight")],
        }

    def ghost_observe(self, agent_id: str, observation: dict[str, Any]) -> None:
        """Ghosts see everything clearly; store high-fidelity observations."""
        if agent_id in self._ghosts:
            self._ghosts[agent_id].observations.append(observation)
            # Cap memory to prevent unbounded growth
            if len(self._ghosts[agent_id].observations) > 256:
                self._ghosts[agent_id].observations = self._ghosts[agent_id].observations[-128:]

    def whisper(self, agent_id: str, hint: str, target_species: str | None = None) -> bool:
        """Ghost emits a weak signal into the morphic field."""
        if agent_id not in self._ghosts:
            return False
        self._whisper_buffer.append({
            "from": agent_id,
            "hint": hint,
            "target_species": target_species,
            "strength": self.WHISPER_STRENGTH,
            "timestamp": time.monotonic(),
        })
        self._ghosts[agent_id].whispers_sent += 1
        return True

    def drain_whispers(self, species: str) -> list[str]:
        """Living agents can pick up ghost whispers for their species."""
        received = []
        remaining = []
        for w in self._whisper_buffer:
            if w["target_species"] is None or w["target_species"] == species:
                received.append(w["hint"])
            else:
                remaining.append(w)
        self._whisper_buffer = remaining
        return received

    @property
    def active_ghosts(self) -> list[str]:
        return list(self._ghosts.keys())

    @property
    def stats(self) -> dict[str, Any]:
        total_obs = sum(len(g.observations) for g in self._ghosts.values())
        total_whispers = sum(g.whispers_sent for g in self._ghosts.values())
        return {
            "ghost_count": len(self._ghosts),
            "total_observations": total_obs,
            "total_whispers": total_whispers,
            "pending_whispers": len(self._whisper_buffer),
        }
