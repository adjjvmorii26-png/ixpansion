"""Agent possession — ghosts override living agents.

A ghost agent can attempt to possess a corporeal agent whose entropy
is below 30%. During possession, the ghost's decision-making replaces
the host's. The host retains fragmentary memories of the experience
and may resist based on willpower.

Possession decays over time; the host gradually regains control.
"""
from __future__ import annotations

import random
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PossessionEvent:
    ghost_id: str
    host_id: str
    host_species: str
    started_tick: int
    strength: float = 1.0       # How firmly the ghost holds control
    host_willpower: float = 0.5 # Host's resistance (species-dependent)
    memories_leaked: list[str] = field(default_factory=list)

    @property
    def is_active(self) -> bool:
        return self.strength > 0.0

    def decay(self, rate: float = 0.05) -> None:
        """Host fights back; possession weakens each tick."""
        resistance = self.host_willpower * rate
        self.strength = max(0.0, self.strength - resistance)


class PossessionManager:
    SPECIES_WILLPOWER: dict[str, float] = {
        "sentinel": 0.8,    # Strong-willed guardians resist well
        "architect": 0.6,
        "wanderer": 0.4,    # Explorers have open minds — easy to possess
    }

    def __init__(self) -> None:
        self._active_possessions: dict[str, PossessionEvent] = {}  # host_id -> event
        self._ghost_registry: dict[str, bool] = {}  # ghost_id -> is_ghost

    def register_ghost(self, ghost_id: str) -> None:
        self._ghost_registry[ghost_id] = True

    def attempt(self, ghost_id: str, host_id: str,
                host_species: str, host_entropy_fraction: float) -> dict[str, Any]:
        """Attempt possession. Requires host entropy below threshold."""
        if ghost_id not in self._ghost_registry:
            return {"success": False, "reason": "not_a_ghost"}
        if host_entropy_fraction > 0.3:
            return {"success": False, "reason": "host_too_vigorous"}
        if host_id in self._active_possessions:
            return {"success": False, "reason": "already_possessed"}

        willpower = self.SPECIES_WILLPOWER.get(host_species, 0.5)
        success_chance = (0.3 - host_entropy_fraction) * 2 * (1.0 - willpower) + 0.3

        rng = random.Random()
        if rng.random() > max(success_chance, 0.05):
            return {"success": False, "reason": "host_resisted", "willpower": willpower}

        event = PossessionEvent(
            ghost_id=ghost_id, host_id=host_id,
            host_species=host_species, started_tick=0,
            host_willpower=willpower,
        )
        self._active_possessions[host_id] = event
        return {"success": True, "willpower": willpower, "initial_strength": 1.0}

    def tick(self, leaked_memories: dict[str, list[str]] | None = None) -> list[dict[str, Any]]:
        """Decay all possessions. Return events that ended this tick."""
        ended = []
        dead_hosts = []

        for host_id, event in self._active_possessions.items():
            event.decay()
            if not event.is_active:
                ended.append({
                    "host": host_id,
                    "ghost": event.ghost_id,
                    "duration_ticks": event.started_tick + 1,
                    "memories": event.memories_leaked,
                })
                dead_hosts.append(host_id)

        for host_id in dead_hosts:
            del self._active_possessions[host_id]
        return ended

    def get_controller(self, host_id: str) -> str | None:
        """Who is actually in control of this agent? Returns ghost_id or None."""
        event = self._active_possessions.get(host_id)
        return event.ghost_id if event and event.is_active else None

    def inject_memory(self, host_id: str, memory: str) -> bool:
        """During possession, the ghost's experiences leak into the host's mind."""
        event = self._active_possessions.get(host_id)
        if not event or not event.is_active:
            return False
        event.memories_leaked.append(memory)
        return True

    @property
    def possessed_agents(self) -> list[str]:
        return [h for h, e in self._active_possessions.items() if e.is_active]

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "active_possessions": len(self.active_possessions),
            "registered_ghosts": len(self._ghost_registry),
            "avg_strength": round(
                sum(e.strength for e in self._active_possessions.values())
                / max(len(self._active_possessions), 1), 4),
        }
