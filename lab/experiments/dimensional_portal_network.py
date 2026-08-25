#!/usr/bin/env python3
"""Dimensional Portal Network — cross-dimensional gateway system.

Bridges portals + topology_engine + non-euclidean geometry to create
a network of dimensional gateways. Agents can step through portals
to traverse between euclidean, hyperbolic, and non-euclidean spaces.

Each portal has a "tuning" that determines what kinds of agents can
pass through, and a "stability" that degrades with use. Unstable
portals may teleport agents to random locations or scatter their
possessions across dimensions.
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
class Portal:
    portal_id: str
    from_dimension: str
    to_dimension: str
    from_position: tuple[float, float]
    to_position: tuple[float, float]
    stability: float = 1.0
    tuning: str = "open"
    uses: int = 0
    max_uses: int = 50
    chaos_tolerance: float = 0.5

    @property
    def is_usable(self) -> bool:
        return self.stability > 0.1 and self.uses < self.max_uses

    @property
    def failure_probability(self) -> float:
        return max(0.0, 1.0 - self.stability)

    def use(self) -> dict[str, Any]:
        self.uses += 1
        self.stability = max(0.0, self.stability - 0.02)
        failed = random.random() > self.stability
        return {"uses": self.uses, "stability": round(self.stability, 3), "failed": failed}


@dataclass
class DimensionTraveler:
    traveler_id: str
    species: str
    current_dimension: str
    position: tuple[float, float]
    entropy: float = 1.0
    possessions: list[str] = field(default_factory=list)
    travel_log: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_stranded(self) -> bool:
        return self.entropy <= 0.0


@dataclass
class DimensionalPortalNetwork:
    """A network of cross-dimensional gateways."""
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._portals: dict[str, Portal] = {}
        self._travelers: dict[str, DimensionTraveler] = {}
        self._transit_log: list[dict[str, Any]] = []
        self._dimension_agents: dict[str, set[str]] = defaultdict(set)
        self._tick = 0

    def create_portal(self, from_dim: str, to_dim: str,
                      from_pos: tuple[float, float] | None = None,
                      to_pos: tuple[float, float] | None = None,
                      tuning: str = "open") -> Portal:
        from_pos = from_pos or (self._rng.uniform(0, 100), self._rng.uniform(0, 100))
        to_pos = to_pos or (self._rng.uniform(0, 100), self._rng.uniform(0, 100))
        pid = hashlib.sha256(
            f"{from_dim}:{to_dim}:{from_pos}:{to_pos}".encode()
        ).hexdigest()[:12]
        portal = Portal(
            portal_id=pid,
            from_dimension=from_dim,
            to_dimension=to_dim,
            from_position=from_pos,
            to_position=to_pos,
            tuning=tuning,
        )
        self._portals[pid] = portal
        return portal

    def add_traveler(self, traveler_id: str, species: str,
                     dimension: str, position: tuple[float, float] | None = None) -> DimensionTraveler:
        position = position or (self._rng.uniform(0, 100), self._rng.uniform(0, 100))
        traveler = DimensionTraveler(
            traveler_id=traveler_id,
            species=species,
            current_dimension=dimension,
            position=position,
        )
        self._travelers[traveler_id] = traveler
        self._dimension_agents[dimension].add(traveler_id)
        return traveler

    def find_portal(self, traveler_id: str, target_dimension: str) -> Portal | None:
        traveler = self._travelers.get(traveler_id)
        if not traveler:
            return None
        for portal in self._portals.values():
            if (portal.from_dimension == traveler.current_dimension
                    and portal.to_dimension == target_dimension
                    and portal.is_usable):
                return portal
        return None

    def transit(self, traveler_id: str, portal_id: str) -> dict[str, Any]:
        traveler = self._travelers.get(traveler_id)
        portal = self._portals.get(portal_id)
        if not traveler or not portal:
            return {"status": "invalid"}
        if not portal.is_usable:
            return {"status": "portal_unusable"}
        if portal.from_dimension != traveler.current_dimension:
            return {"status": "wrong_dimension"}

        result = portal.use()
        old_dim = traveler.current_dimension

        if result["failed"]:
            # Chaos transit: scattered to random dimension
            dims = ["euclidean", "hyperbolic", "non_euclid"]
            new_dim = self._rng.choice(dims)
            new_pos = (self._rng.uniform(0, 100), self._rng.uniform(0, 100))
            scattered = traveler.possessions[:self._rng.randint(0, len(traveler.possessions))]
            traveler.possessions = [p for p in traveler.possessions if p not in scattered]
        else:
            new_dim = portal.to_dimension
            new_pos = portal.to_position

        self._dimension_agents[old_dim].discard(traveler_id)
        traveler.current_dimension = new_dim
        traveler.position = new_pos
        traveler.entropy = max(0.0, traveler.entropy - 0.05)
        self._dimension_agents[new_dim].add(traveler_id)

        event = {
            "tick": self._tick,
            "traveler": traveler_id,
            "from_dimension": old_dim,
            "to_dimension": new_dim,
            "from_pos": traveler.travel_log[-1]["position"] if traveler.travel_log else [0, 0],
            "to_pos": list(new_pos),
            "failed": result["failed"],
            "portal_stability": result["stability"],
        }
        traveler.travel_log.append({
            "dimension": new_dim,
            "position": list(new_pos),
            "tick": self._tick,
        })
        self._transit_log.append(event)
        return event

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        # Natural stability recovery for unused portals
        for portal in self._portals.values():
            if portal.uses == 0 or self._rng.random() > 0.7:
                portal.stability = min(1.0, portal.stability + 0.01)
        return {"tick": self._tick}

    def network_map(self) -> dict[str, Any]:
        connections: dict[str, list[str]] = defaultdict(list)
        for portal in self._portals.values():
            if portal.is_usable:
                connections[portal.from_dimension].append(portal.to_dimension)

        return {
            "dimensions": list(self._dimension_agents.keys()),
            "portal_count": len(self._portals),
            "usable_portals": sum(1 for p in self._portals.values() if p.is_usable),
            "connections": {k: list(set(v)) for k, v in connections.items()},
            "agents_per_dimension": {
                dim: len(agents) for dim, agents in self._dimension_agents.items()
            },
            "transit_count": len(self._transit_log),
            "failed_transits": sum(1 for t in self._transit_log if t["failed"]),
        }


def demo() -> dict[str, Any]:
    network = DimensionalPortalNetwork(seed=42)

    # Create dimensional portals
    network.create_portal("euclidean", "hyperbolic")
    network.create_portal("hyperbolic", "non_euclid")
    network.create_portal("non_euclid", "euclidean")
    network.create_portal("euclidean", "non_euclid")
    network.create_portal("hyperbolic", "euclidean")

    # Add travelers
    for i in range(8):
        dim = ["euclidean", "hyperbolic", "non_euclid"][i % 3]
        network.add_traveler(f"traveler-{i}", ["sentinel", "architect", "wanderer"][i % 3], dim)

    # Simulate travel
    for tick in range(15):
        network.tick()
        for traveler_id in list(network._travelers.keys()):
            traveler = network._travelers[traveler_id]
            if traveler.is_stranded:
                continue
            target_dims = ["euclidean", "hyperbolic", "non_euclid"]
            target = random.Random(tick * 10 + hash(traveler_id)).choice(target_dims)
            portal = network.find_portal(traveler_id, target)
            if portal:
                network.transit(traveler_id, portal.portal_id)

    return network.network_map()


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
