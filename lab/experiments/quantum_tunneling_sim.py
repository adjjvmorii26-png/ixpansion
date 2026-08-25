#!/usr/bin/env python3
"""Quantum Tunneling Simulator — social barrier erosion through collective attempts.

Bridges quantum_tunneling + consensus_reality + panopticon to model how
social barriers dissolve as more people challenge them. Each barrier has
integrity that weakens with collective attempts. The environment reshapes
itself around successful tunnelers.

This creates a model of social change: barriers that seem permanent
can dissolve when enough people push through them.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Barrier:
    barrier_id: str
    position: tuple[float, float]
    thickness: float
    integrity: float = 1.0
    total_attempts: int = 0
    successful_tunnels: int = 0
    terrain_effect: str = "impassable"

    @property
    def is_dissolved(self) -> bool:
        return self.integrity <= 0.0

    @property
    def tunnel_probability(self) -> float:
        collective = min(0.5, self.total_attempts * 0.02)
        return min(0.95, (1.0 / max(1.0, self.thickness)) * self.integrity + collective)


@dataclass
class TunnelAgent:
    agent_id: str
    curiosity: float
    position: tuple[float, float]
    tunnels_attempted: int = 0
    tunnels_successful: int = 0
    energy: float = 1.0


@dataclass
class QuantumTunnelingSim:
    """Social barrier erosion simulation."""
    width: int = 16
    height: int = 16
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._barriers: dict[str, Barrier] = {}
        self._agents: dict[str, TunnelAgent] = {}
        self._terrain: dict[tuple[int, int], str] = {}
        self._tick = 0
        self._events: list[dict[str, Any]] = []

    def create_barrier(self, x: int, y: int, thickness: float = 10.0) -> str:
        bid = hashlib.sha256(f"{x}:{y}:{self._tick}".encode()).hexdigest()[:10]
        self._barriers[bid] = Barrier(
            barrier_id=bid, position=(x, y), thickness=thickness
        )
        return bid

    def add_agent(self, agent_id: str, curiosity: float) -> TunnelAgent:
        pos = (self._rng.randint(0, self.width - 1), self._rng.randint(0, self.height - 1))
        agent = TunnelAgent(agent_id=agent_id, curiosity=curiosity, position=pos)
        self._agents[agent_id] = agent
        return agent

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        new_events: list[dict[str, Any]] = []

        for agent in self._agents.values():
            if agent.energy <= 0:
                continue

            # Find nearby barriers
            for bid, barrier in self._barriers.items():
                if barrier.is_dissolved:
                    continue
                dist = math.dist(agent.position, barrier.position)
                if dist > 3:
                    continue

                barrier.total_attempts += 1
                agent.tunnels_attempted += 1
                agent.energy -= 0.05

                # Tunnel check
                prob = barrier.tunnel_probability * agent.curiosity
                if self._rng.random() < prob:
                    barrier.successful_tunnels += 1
                    barrier.integrity = max(0.0, barrier.integrity - 0.15)
                    agent.tunnels_successful += 1
                    agent.energy = min(1.0, agent.energy + 0.1)

                    event = {
                        "tick": self._tick,
                        "agent": agent.agent_id,
                        "barrier": bid,
                        "integrity_after": round(barrier.integrity, 3),
                        "dissolved": barrier.is_dissolved,
                    }
                    new_events.append(event)
                    self._events.append(event)

                    # Terrain reshapes
                    pos = barrier.position
                    self._terrain[(int(pos[0]), int(pos[1]))] = (
                        "open" if barrier.is_dissolved else "weakened"
                    )

        # Natural energy recovery
        for agent in self._agents.values():
            agent.energy = min(1.0, agent.energy + 0.02)

        return {
            "tick": self._tick,
            "new_events": len(new_events),
            "active_barriers": sum(1 for b in self._barriers.values() if not b.is_dissolved),
            "dissolved_barriers": sum(1 for b in self._barriers.values() if b.is_dissolved),
        }

    def report(self) -> dict[str, Any]:
        agent_stats = {}
        for aid, agent in self._agents.items():
            agent_stats[aid] = {
                "tunnels_attempted": agent.tunnels_attempted,
                "tunnels_successful": agent.tunnels_successful,
                "success_rate": round(
                    agent.tunnels_successful / max(1, agent.tunnels_attempted), 3
                ),
            }

        return {
            "barriers": {
                bid: {
                    "integrity": round(b.integrity, 3),
                    "attempts": b.total_attempts,
                    "tunnels": b.successful_tunnels,
                    "dissolved": b.is_dissolved,
                }
                for bid, b in self._barriers.items()
            },
            "agents": agent_stats,
            "terrain_changes": len(self._terrain),
            "total_events": len(self._events),
        }


def demo() -> dict[str, Any]:
    sim = QuantumTunnelingSim(seed=42)
    # Create barriers
    b1 = sim.create_barrier(5, 5, thickness=8.0)
    b2 = sim.create_barrier(10, 10, thickness=12.0)
    b3 = sim.create_barrier(8, 3, thickness=6.0)

    # Create agents with varying curiosity
    for i in range(10):
        sim.add_agent(f"agent-{i}", curiosity=0.3 + (i * 0.07))

    for _ in range(30):
        sim.tick()

    return sim.report()


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
