"""Morphic resonance field.

A shared knowledge substrate that propagates insights between agents
of the same species. When an agent consolidates a new semantic memory,
the field broadcasts a weakened echo to all resonating agents. This
creates emergent collective learning without direct communication.
"""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResonanceEcho:
    source_agent: str
    species: str
    knowledge_key: str
    knowledge_value: Any
    strength: float


class MorphicField:
    def __init__(self) -> None:
        self._field: dict[str, list[ResonanceEcho]] = defaultdict(list)
        self._species_map: dict[str, str] = {}

    def attune(self, agent_id: str, species: str) -> None:
        self._species_map[agent_id] = species

    def broadcast(self, agent_id: str, key: str, value: Any, radius: float = 1.0) -> int:
        """Broadcast an insight from one agent to its species cohort.
        Returns number of agents that received the echo."""
        species = self._species_map.get(agent_id, "")
        if not species:
            return 0

        delivered = 0
        for other_id, other_species in self._species_map.items():
            if other_id == agent_id or other_species != species:
                continue
            # Strength falls off with distance (simulated as inverse square)
            strength = min(1.0, radius / max(len(self._species_map), 1))
            echo = ResonanceEcho(
                source_agent=agent_id,
                species=species,
                knowledge_key=key,
                knowledge_value=value,
                strength=round(strength, 4),
            )
            self._field[other_id].append(echo)
            # Cap echoes per agent to prevent flooding
            if len(self._field[other_id]) > 32:
                self._field[other_id] = self._field[other_id][-32:]
            delivered += 1

        return delivered

    def receive(self, agent_id: str) -> list[ResonanceEcho]:
        """Retrieve and clear pending echoes for an agent."""
        echoes = self._field.get(agent_id, [])
        self._field[agent_id] = []
        return echoes

    @property
    def coherence(self) -> float:
        """How synchronized the field is across species."""
        total_agents = len(self._species_map)
        if total_agents < 2:
            return 0.0
        species_counts = defaultdict(int)
        for s in self._species_map.values():
            species_counts[s] += 1
        dominant = max(species_counts.values())
        return round(dominant / total_agents, 3)

    @property
    def pending_echoes(self) -> dict[str, int]:
        return {k: len(v) for k, v in self._field.items() if v}
