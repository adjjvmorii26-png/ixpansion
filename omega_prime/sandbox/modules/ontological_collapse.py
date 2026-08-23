"""Ontological collapse — phase transition of shared reality.

When >60% of observed cells are stuck in ambiguous superposition,
the system becomes critically unstable. At the next tick, ALL
ambiguous cells simultaneously collapse to random resolutions —
a reality cascade that rewrites the map's consensus in one pulse.

Agents near collapsing cells experience "ontological shock" (temporary
entropy spike). Agents who predicted the correct resolution gain
massive credibility.
"""
from __future__ import annotations

import random
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CollapseEvent:
    event_id: str
    tick: int
    cells_collapsed: int
    total_ambiguous_before: int
    shock_radius: float
    affected_agents: list[str] = field(default_factory=list)

    @property
    def magnitude(self) -> float:
        return min(1.0, self.cells_collapsed / max(self.total_ambiguous_before, 1))


class OntologicalCollapseEngine:
    CRITICAL_THRESHOLD = 0.6    # Fraction of ambiguous cells before cascade
    SHOCK_RADIUS = 3.0          # Distance within which agents feel the shock
    ENTROPY_SHOCK = 15.0        # Entropy cost of being near a collapse

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._ambiguity_map: dict[tuple[int, int], set[str]] = {}
        self._consolidated: dict[tuple[int, int], str] = {}
        self._collapse_history: list[CollapseEvent] = []
        self._tick = 0
        self._agents_positions: dict[str, tuple[float, float]] = {}

    def register_agent_position(self, agent_id: str, pos: tuple[float, float]) -> None:
        self._agents_positions[agent_id] = pos

    def add_ambiguity(self, pos: tuple[int, int], possible_states: set[str]) -> None:
        self._ambiguity_map[pos] = possible_states

    def resolve_cell_manually(self, pos: tuple[int, int], truth: str) -> bool:
        self._ambiguity_map.pop(pos, None)
        self._consolidated[pos] = truth
        return True

    @property
    def ambiguity_ratio(self) -> float:
        """Fraction of tracked cells currently in ambiguous state."""
        total = len(self._ambiguity_map) + len(self._consolidated)
        return len(self._ambiguity_map) / max(total, 1)

    @property
    def is_critical(self) -> bool:
        return self.ambiguity_ratio >= self.CRITICAL_THRESHOLD and len(self._ambiguity_map) >= 5

    def tick(self) -> dict[str, Any]:
        """Check for critical mass; trigger cascade if threshold exceeded."""
        self._tick += 1

        if not self.is_critical:
            return {"tick": self._tick, "cascade": False,
                    "ambiguity_ratio": round(self.ambiguity_ratio, 4),
                    "critical": False}

        # CASCADE!
        collapsed_cells = {}
        for pos, states in self._ambiguity_map.items():
            chosen = self._rng.choice(list(states))
            collapsed_cells[pos] = chosen
            self._consolidated[pos] = chosen

        # Find agents in shock radius of any collapsed cell
        shocked_agents = []
        for agent_id, agent_pos in self._agents_positions.items():
            for cell_pos in collapsed_cells:
                dx = agent_pos[0] - cell_pos[0]
                dy = agent_pos[1] - cell_pos[1]
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist <= self.SHOCK_RADIUS:
                    shocked_agents.append(agent_id)
                    break

        event_id = hashlib.sha256(f"{self._tick}:{len(collapsed_cells)}".encode()).hexdigest()[:12]
        event = CollapseEvent(
            event_id=event_id, tick=self._tick,
            cells_collapsed=len(collapsed_cells),
            total_ambiguous_before=len(self._ambiguity_map),
            shock_radius=self.SHOCK_RADIUS,
            affected_agents=list(set(shocked_agents)),
        )
        self._collapse_history.append(event)
        self._ambiguity_map.clear()

        return {
            "tick": self._tick,
            "cascade": True,
            "event_id": event.event_id[:8],
            "cells_resolved": event.cells_collapsed,
            "magnitude": round(event.magnitude, 4),
            "shocked_agents": event.affected_agents,
            "shock_count": len(event.affected_agents),
        }

    @property
    def consolidated_map(self) -> dict[str, str]:
        return {f"{k[0]},{k[1]}": v for k, v in sorted(self._consolidated.items())}

    @property
    def stats(self) -> dict[str, Any]:
        total_collapse_events = len(self._collapse_history)
        avg_magnitude = (
            sum(e.magnitude for e in self._collapse_history) / max(total_collapse_events, 1)
        )
        return {
            "tracked_cells": len(self._ambiguity_map) + len(self._consolidated),
            "ambiguous_cells": len(self._ambiguity_map),
            "consolidated_cells": len(self._consolidated),
            "ambiguity_ratio": round(self.ambiguity_ratio, 4),
            "is_critical": self.is_critical,
            "total_cascades": total_collapse_events,
            "avg_cascade_magnitude": round(avg_magnitude, 4),
        }
