#!/usr/bin/env python3
"""Morphic Resonance Lattice — knowledge propagation through geometric spaces.

Bridges morphic_field + lattice dimensions (euclidean, hyperbolic, non-euclidean)
to model how insights spread differently depending on the geometry of the space.

In euclidean space, knowledge decays linearly with distance.
In hyperbolic space, knowledge reaches exponentially more agents.
In non-euclidean space, knowledge can arrive via unexpected shortcuts.

This reveals how the structure of a network determines what its
inhabitants can collectively learn.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Insight:
    insight_id: str
    source_agent: str
    species: str
    key: str
    value: str
    strength: float
    origin_tick: int

    def payload(self) -> dict[str, Any]:
        return {
            "insight_id": self.insight_id,
            "source": self.source_agent,
            "species": self.species,
            "key": self.key,
            "strength": round(self.strength, 4),
            "tick": self.origin_tick,
        }


@dataclass
class LatticeAgent:
    agent_id: str
    species: str
    position: tuple[float, float]
    received_insights: list[Insight] = field(default_factory=list)
    broadcast_count: int = 0

    def knows(self, key: str) -> bool:
        return any(i.key == key for i in self.received_insights)


@dataclass
class MorphicLattice:
    """Knowledge propagation across different geometric spaces."""
    width: float = 100.0
    height: float = 100.0
    curvature: float = -1.0
    warp_factor: float = 0.3
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._agents: dict[str, LatticeAgent] = {}
        self._tick = 0
        self._propagation_log: list[dict[str, Any]] = []
        self._insight_registry: dict[str, Insight] = {}

    def register_agent(self, agent_id: str, species: str,
                       position: tuple[float, float] | None = None) -> LatticeAgent:
        if position is None:
            position = (
                self._rng.uniform(0, self.width),
                self._rng.uniform(0, self.height),
            )
        agent = LatticeAgent(agent_id=agent_id, species=species, position=position)
        self._agents[agent_id] = agent
        return agent

    def broadcast_insight(self, agent_id: str, key: str, value: str,
                          geometry: str = "euclidean") -> list[str]:
        """Broadcast an insight; returns list of recipient agent_ids."""
        source = self._agents.get(agent_id)
        if not source:
            return []

        insight = Insight(
            insight_id=hashlib.sha256(f"{agent_id}:{key}:{self._tick}".encode()).hexdigest()[:12],
            source_agent=agent_id,
            species=source.species,
            key=key,
            value=value,
            strength=1.0,
            origin_tick=self._tick,
        )
        source.broadcast_count += 1
        self._insight_registry[insight.insight_id] = insight

        recipients: list[str] = []
        for other_id, other in self._agents.items():
            if other_id == agent_id:
                continue
            if other.species != source.species:
                continue
            if other.knows(key):
                continue

            dist = self._distance(source.position, other.position, geometry)
            max_range = self._range_for_geometry(geometry)
            if dist > max_range:
                continue

            # Signal attenuation depends on geometry
            attenuation = self._attenuation(dist, max_range, geometry)
            received = Insight(
                insight_id=f"{insight.insight_id}:{other_id}",
                source_agent=agent_id,
                species=source.species,
                key=key,
                value=value,
                strength=round(insight.strength * attenuation, 4),
                origin_tick=self._tick,
            )
            other.received_insights.append(received)
            recipients.append(other_id)

        self._propagation_log.append({
            "tick": self._tick,
            "source": agent_id,
            "geometry": geometry,
            "recipients": len(recipients),
            "key": key,
        })
        return recipients

    def tick(self, geometry: str = "euclidean") -> dict[str, Any]:
        self._tick += 1
        # Decay insight strengths
        for agent in self._agents.values():
            agent.received_insights = [
                Insight(
                    insight_id=i.insight_id,
                    source_agent=i.source_agent,
                    species=i.species,
                    key=i.key,
                    value=i.value,
                    strength=max(0.0, i.strength - 0.02),
                    origin_tick=i.origin_tick,
                )
                for i in agent.received_insights
                if i.strength > 0.02
            ]
        return {"tick": self._tick, "agents": len(self._agents)}

    def _distance(self, a: tuple[float, float], b: tuple[float, float],
                  geometry: str) -> float:
        base = math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
        if geometry == "hyperbolic":
            # Hyperbolic distance grows slower, so agents feel closer
            return base * 0.6
        elif geometry == "non_euclid":
            # Warp adds random shortcuts
            warp = 1.0 + self.warp_factor * math.sin(a[0] + b[1])
            return base * abs(1.0 / warp)
        return base

    def _range_for_geometry(self, geometry: str) -> float:
        if geometry == "hyperbolic":
            return self.width * 1.5  # Hyperbolic space has more room
        elif geometry == "non_euclid":
            return self.width * 0.8  # Warps can shortcut
        return self.width * 0.5  # Euclidean baseline

    def _attenuation(self, dist: float, max_range: float, geometry: str) -> float:
        ratio = dist / max_range
        if geometry == "hyperbolic":
            return max(0.1, 1.0 - ratio * 0.3)  # Slow decay
        elif geometry == "non_euclid":
            return max(0.05, 1.0 - ratio * 0.5)  # Moderate with noise
        return max(0.0, 1.0 - ratio)  # Linear decay

    def propagation_summary(self) -> dict[str, Any]:
        geo_stats: dict[str, dict[str, float]] = defaultdict(lambda: {"total": 0, "recipients": 0})
        for entry in self._propagation_log:
            geo = entry["geometry"]
            geo_stats[geo]["total"] += 1
            geo_stats[geo]["recipients"] += entry["recipients"]

        result = {}
        for geo, stats in geo_stats.items():
            avg = stats["recipients"] / stats["total"] if stats["total"] else 0
            result[geo] = {
                "broadcasts": stats["total"],
                "total_recipients": stats["recipients"],
                "avg_recipients": round(avg, 2),
            }
        return result


def demo() -> dict[str, Any]:
    lattice = MorphicLattice(seed=42)

    # Create 20 agents of 3 species across the space
    species_list = ["sentinel", "architect", "wanderer"]
    for i in range(20):
        lattice.register_agent(
            f"agent-{i}",
            species_list[i % 3],
        )

    # Run 10 ticks for each geometry, broadcasting insights
    results = {}
    for geometry in ["euclidean", "hyperbolic", "non_euclid"]:
        # Reset agents for fair comparison
        for agent in lattice._agents.values():
            agent.received_insights.clear()
            agent.broadcast_count = 0
        lattice._propagation_log.clear()

        for tick in range(10):
            lattice.tick(geometry)
            # Each species broadcasts one insight per tick
            for species in species_list:
                species_agents = [
                    a for a in lattice._agents.values() if a.species == species
                ]
                if species_agents:
                    broadcaster = species_agents[tick % len(species_agents)]
                    lattice.broadcast_insight(
                        broadcaster.agent_id,
                        f"insight-{species}-{tick}",
                        f"discovery from {species}",
                        geometry,
                    )

        results[geometry] = lattice.propagation_summary().get(geometry, {})

    return {"geometry_comparison": results}


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
