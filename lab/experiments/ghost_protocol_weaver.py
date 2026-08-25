#!/usr/bin/env python3
"""Ghost Protocol Weaver — agents haunt, possess, and symbiose.

Bridges ghost_protocol + possession + symbiosis to model the full
lifecycle of agent death, ghosting, haunting, possession, and
symbiotic coexistence.

When an agent exhausts its entropy budget, it becomes a ghost. Ghosts
can haunt locations (marking them as spiritually charged), attempt to
possess weakened living agents, or form symbiotic bonds where two agents
share a body. This creates a rich meta-game around life, death, and
the spaces between.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


class AgentState:
    CORPOREAL = "corporeal"
    GHOST = "ghost"
    POSSESSED = "possessed"
    SYMBIOTIC = "symbiotic"


@dataclass
class GhostWeaverAgent:
    agent_id: str
    species: str
    state: str = AgentState.CORPOREAL
    entropy: float = 1.0
    willpower: float = 0.5
    position: tuple[float, float] = (0.0, 0.0)
    ghost_knowledge: list[str] = field(default_factory=list)
    haunting_sites: set[tuple[int, int]] = field(default_factory=set)
    symbiont_id: str | None = None
    possessed_by: str | None = None

    @property
    def is_alive(self) -> bool:
        return self.state == AgentState.CORPOREAL

    @property
    def is_ghost(self) -> bool:
        return self.state == AgentState.GHOST

    @property
    def is_accessible(self) -> bool:
        return self.state in (AgentState.CORPOREAL, AgentState.POSSESSED)

    def entropy_cost(self, amount: float) -> bool:
        """Spend entropy. Returns False if depleted."""
        self.entropy = max(0.0, self.entropy - amount)
        if self.entropy <= 0.0 and self.is_alive:
            self.state = AgentState.GHOST
            return False
        return True

    def regenerate(self, amount: float) -> None:
        self.entropy = min(1.0, self.entropy + amount)


@dataclass
class HauntingSite:
    site_id: str
    position: tuple[int, int]
    haunters: set[str] = field(default_factory=set)
    spiritual_charge: float = 0.0
    age: int = 0

    @property
    def is_active(self) -> bool:
        return self.spiritual_charge > 0.1

    def decay(self, rate: float = 0.05) -> None:
        self.spiritual_charge = max(0.0, self.spiritual_charge - rate)
        self.age += 1


@dataclass
class SymbioticBond:
    bond_id: str
    agent_a: str
    agent_b: str
    compatibility: float = 0.5
    harmony: float = 0.5
    shared_knowledge: list[str] = field(default_factory=list)
    formed_tick: int = 0

    @property
    def is_stable(self) -> bool:
        return self.harmony > 0.3

    def interact(self) -> float:
        """Simulate one tick of interaction; returns harmony change."""
        delta = self.compatibility * 0.1 - (1 - self.harmony) * 0.05
        self.harmony = max(0.0, min(1.0, self.harmony + delta))
        return delta


@dataclass
class GhostProtocolWeaver:
    """Manages the full ghost/possess/symbiosis lifecycle."""
    resurrection_threshold: float = 0.15
    possession_decay_rate: float = 0.05
    haunting_charge_per_tick: float = 0.1
    symbiosis_compatibility_bonus: float = 0.1
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._agents: dict[str, GhostWeaverAgent] = {}
        self._hauntings: dict[str, HauntingSite] = {}
        self._symbioses: dict[str, SymbioticBond] = {}
        self._events: list[dict[str, Any]] = []
        self._tick = 0

    def add_agent(self, agent_id: str, species: str,
                  position: tuple[float, float] | None = None) -> GhostWeaverAgent:
        if position is None:
            position = (self._rng.uniform(0, 50), self._rng.uniform(0, 50))
        willpower_map = {"sentinel": 0.8, "architect": 0.6, "wanderer": 0.4}
        agent = GhostWeaverAgent(
            agent_id=agent_id,
            species=species,
            position=position,
            willpower=willpower_map.get(species, 0.5),
        )
        self._agents[agent_id] = agent
        return agent

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        events: list[dict[str, Any]] = []

        # Ghost regeneration
        for agent in self._agents.values():
            if agent.is_ghost:
                agent.regenerate(0.03)
                if agent.entropy >= self.resurrection_threshold:
                    agent.state = AgentState.CORPOREAL
                    events.append({
                        "type": "resurrection",
                        "agent": agent.agent_id,
                        "tick": self._tick,
                    })

        # Possession decay
        for agent in self._agents.values():
            if agent.state == AgentState.POSSESSED and agent.possessed_by:
                ghost = self._agents.get(agent.possessed_by)
                if ghost:
                    ghost.state = AgentState.CORPOREAL
                    agent.possessed_by = None
                    agent.state = AgentState.CORPOREAL
                    events.append({
                        "type": "possession_ended",
                        "host": agent.agent_id,
                        "ghost": ghost.agent_id,
                        "tick": self._tick,
                    })

        # Haunting site decay
        for site in self._hauntings.values():
            site.decay()

        # Symbiosis interaction
        for bond in self._symbioses.values():
            delta = bond.interact()
            if not bond.is_stable:
                events.append({
                    "type": "symbiosis_broken",
                    "agents": [bond.agent_a, bond.agent_b],
                    "harmony": round(bond.harmony, 3),
                    "tick": self._tick,
                })

        self._events.extend(events)
        return {"tick": self._tick, "events": events}

    def ghost_haunt(self, ghost_id: str, position: tuple[int, int]) -> dict[str, Any]:
        ghost = self._agents.get(ghost_id)
        if not ghost or not ghost.is_ghost:
            return {"status": "not_ghost"}

        key = f"{position[0]},{position[1]}"
        if key not in self._hauntings:
            self._hauntings[key] = HauntingSite(
                site_id=hashlib.sha256(key.encode()).hexdigest()[:8],
                position=position,
            )
        site = self._hauntings[key]
        site.haunters.add(ghost_id)
        site.spiritual_charge += self.haunting_charge_per_tick
        ghost.haunting_sites.add(position)

        return {"status": "haunting", "charge": round(site.spiritual_charge, 3)}

    def ghost_possess(self, ghost_id: str, host_id: str) -> dict[str, Any]:
        ghost = self._agents.get(ghost_id)
        host = self._agents.get(host_id)
        if not ghost or not host:
            return {"status": "unknown"}
        if not ghost.is_ghost:
            return {"status": "not_ghost"}
        if not host.is_alive or host.entropy > 0.3:
            return {"status": "host_too_strong"}

        # Possession check: ghost power vs host willpower
        ghost_power = ghost.entropy * 2
        if ghost_power > host.willpower:
            host.state = AgentState.POSSESSED
            host.possessed_by = ghost_id
            ghost.state = AgentState.CORPOREAL
            event = {
                "type": "possession",
                "ghost": ghost_id,
                "host": host_id,
                "ghost_power": round(ghost_power, 3),
                "host_willpower": host.willpower,
                "tick": self._tick,
            }
            self._events.append(event)
            return {"status": "possessed", "event": event}
        return {"status": "resisted", "ghost_power": round(ghost_power, 3)}

    def form_symbiosis(self, agent_a_id: str, agent_b_id: str) -> dict[str, Any]:
        a = self._agents.get(agent_a_id)
        b = self._agents.get(agent_b_id)
        if not a or not b or not a.is_alive or not b.is_alive:
            return {"status": "invalid"}

        dist = math.dist(a.position, b.position)
        compatibility = max(0.1, 1.0 - dist / 50.0)
        if a.species == b.species:
            compatibility = min(1.0, compatibility + self.symbiosis_compatibility_bonus)

        if compatibility < 0.2:
            return {"status": "incompatible", "compatibility": round(compatibility, 3)}

        bond_id = hashlib.sha256(
            f"{agent_a_id}:{agent_b_id}:{self._tick}".encode()
        ).hexdigest()[:12]
        bond = SymbioticBond(
            bond_id=bond_id,
            agent_a=agent_a_id,
            agent_b=agent_b_id,
            compatibility=compatibility,
            formed_tick=self._tick,
        )
        self._symbioses[bond_id] = bond
        a.symbiont_id = agent_b_id
        b.symbiont_id = agent_a_id
        a.state = AgentState.SYMBIOTIC
        b.state = AgentState.SYMBIOTIC

        return {"status": "bonded", "bond_id": bond_id, "compatibility": round(compatibility, 3)}

    def census(self) -> dict[str, Any]:
        states = defaultdict(int)
        for agent in self._agents.values():
            states[agent.state] += 1
        return {
            "total_agents": len(self._agents),
            "states": dict(states),
            "haunting_sites": sum(1 for s in self._hauntings.values() if s.is_active),
            "symbiotic_bonds": len(self._symbioses),
            "total_events": len(self._events),
        }


def demo() -> dict[str, Any]:
    weaver = GhostProtocolWeaver(seed=42)
    species = ["sentinel", "architect", "wanderer"]

    for i in range(12):
        weaver.add_agent(f"agent-{i}", species[i % 3])

    # Deplete some agents to trigger ghosting
    for i in range(4):
        agent = weaver._agents[f"agent-{i}"]
        agent.entropy = 0.01
        agent.state = AgentState.GHOST

    # Simulate 20 ticks
    for _ in range(20):
        weaver.tick()

    # Ghosts haunt
    weaver.ghost_haunt("agent-0", (5, 5))
    weaver.ghost_haunt("agent-1", (10, 10))
    weaver.ghost_haunt("agent-2", (5, 5))

    # Attempt possession
    weaver.ghost_possess("agent-3", "agent-8")
    weaver.ghost_possess("agent-0", "agent-9")

    # Form symbiosis
    weaver.form_symbiosis("agent-4", "agent-5")
    weaver.form_symbiosis("agent-10", "agent-11")

    return weaver.census()


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
