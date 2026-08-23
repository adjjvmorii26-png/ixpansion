"""Metamorphosis protocol — agents evolve new capabilities mid-lifetime.

When an agent accumulates enough diverse experiences, it can undergo
metamorphosis: acquiring a new trait, changing its species classification,
or unlocking abilities it didn't have at spawn.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from .base_agent import BaseAgent
from .agent_traits import TraitSet, TRAIT_LIBRARY


@dataclass
class MetamorphEvent:
    agent_id: str
    from_species: str
    to_species: str
    traits_gained: list[str]
    trigger: str
    tick: int


class MetamorphProtocol:
    MIN_EXPERIENCE_DIVERSITY = 5   # Unique action types needed
    METAMORPHOSIS_COST = 30.0      # Energy required

    def __init__(self) -> None:
        self._experience_counter: dict[str, Counter[str]] = {}
        self._history: list[MetamorphEvent] = []

    def record_experience(self, agent: BaseAgent, action_type: str) -> int:
        """Track what an agent has done; returns total unique experience types."""
        if agent.state.agent_id not in self._experience_counter:
            self._experience_counter[agent.state.agent_id] = Counter()
        self._experience_counter[agent.state.agent_id][action_type] += 1
        return len(self._experience_counter[agent.state.agent_id])

    def attempt_metamorphosis(self, agent: BaseAgent,
                              target_traits: list[str],
                              new_species: str | None = None,
                              tick: int = 0) -> MetamorphEvent | None:
        """Attempt to evolve the agent. Requires diversity + energy."""
        unique_exp = len(self._experience_counter.get(agent.state.agent_id, {}))
        if unique_exp < self.MIN_EXPERIENCE_DIVERSITY:
            return None
        if agent.state.energy < self.METAMORPHOSIS_COST:
            return None

        # Apply cost and gain traits
        agent.drain_energy(self.METAMORPHOSIS_COST)
        gained = []
        if hasattr(agent, 'traits'):
            for t in target_traits:
                if agent.traits.add(t):
                    gained.append(t)

        old_species = agent.state.species
        if new_species:
            agent.state.species = new_species

        event = MetamorphEvent(
            agent_id=agent.state.agent_id,
            from_species=old_species,
            to_species=agent.state.species,
            traits_gained=gained,
            trigger=f"diversity={unique_exp}",
            tick=tick,
        )
        self._history.append(event)
        return event

    @property
    def metamorph_history(self) -> list[dict[str, Any]]:
        return [
            {"agent": e.agent_id[:8], "from": e.from_species, "to": e.to_species,
             "traits": e.traits_gained}
            for e in self._history
        ]
