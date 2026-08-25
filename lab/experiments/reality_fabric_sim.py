#!/usr/bin/env python3
"""Reality Fabric Simulator — model the substrate of shared reality.

Bridges reality_fabric + dimensional_fold + ontological_collapse to
simulate the fabric that holds shared reality together. The fabric
has tension (how stretched reality is), opacity (how transparent
the underlying void is), and weave (how tightly reality is held).

When tension exceeds the fabric's strength, reality folds —
dimensions collapse into each other, creating hybrid zones.
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
class FabricCell:
    position: tuple[int, int]
    tension: float = 0.0
    opacity: float = 0.8
    weave_density: float = 0.5
    dimension: str = "primary"
    folded: bool = False
    fold_target: str | None = None

    @property
    def strength(self) -> float:
        return self.weave_density * self.opacity

    @property
    def is_stressed(self) -> bool:
        return self.tension > self.strength

    @property
    def fold_risk(self) -> float:
        if self.strength == 0:
            return 1.0
        return min(1.0, self.tension / self.strength)


@dataclass
class RealityFabricSim:
    """Simulate the fabric of shared reality."""
    width: int = 12
    height: int = 12
    fold_threshold: float = 0.9
    tension_per_agent: float = 0.05
    decay_rate: float = 0.02
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._cells: dict[tuple[int, int], FabricCell] = {}
        self._agents: dict[str, dict[str, Any]] = {}
        self._tick = 0
        self._fold_events: list[dict[str, Any]] = []

    def init_fabric(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                self._cells[(x, y)] = FabricCell(
                    position=(x, y),
                    weave_density=self._rng.uniform(0.3, 0.8),
                    opacity=self._rng.uniform(0.5, 1.0),
                )

    def add_agent(self, agent_id: str, dimension: str = "primary",
                  position: tuple[int, int] | None = None) -> None:
        if position is None:
            position = (self._rng.randint(0, self.width - 1),
                       self._rng.randint(0, self.height - 1))
        self._agents[agent_id] = {"dimension": dimension, "position": position}

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        new_folds: list[dict[str, Any]] = []

        # Agents exert tension
        for agent_id, agent in self._agents.items():
            x, y = agent["position"]
            # Move randomly
            dx = self._rng.randint(-1, 1)
            dy = self._rng.randint(-1, 1)
            new_x = (x + dx) % self.width
            new_y = (y + dy) % self.height
            agent["position"] = (new_x, new_y)

            # Exert tension on current and adjacent cells
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    cx = (new_x + dx) % self.width
                    cy = (new_y + dy) % self.height
                    cell = self._cells.get((cx, cy))
                    if cell:
                        cell.tension += self.tension_per_agent / (1 + abs(dx) + abs(dy))

        # Natural tension decay
        for cell in self._cells.values():
            cell.tension = max(0.0, cell.tension - self.decay_rate)

        # Check for folds
        for pos, cell in self._cells.items():
            if cell.fold_risk >= self.fold_threshold and not cell.folded:
                # Fold: merge with a random neighbor's dimension
                neighbors = []
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = (pos[0] + dx) % self.width, (pos[1] + dy) % self.height
                    ncell = self._cells.get((nx, ny))
                    if ncell and ncell.dimension != cell.dimension:
                        neighbors.append(ncell)

                if neighbors:
                    target = self._rng.choice(neighbors)
                    cell.folded = True
                    cell.fold_target = target.dimension
                    cell.tension = 0.0
                    # The fold creates a hybrid
                    event = {
                        "tick": self._tick,
                        "position": list(pos),
                        "from_dim": cell.dimension,
                        "to_dim": target.dimension,
                        "fold_risk_at_fold": round(cell.fold_risk, 3),
                    }
                    new_folds.append(event)
                    self._fold_events.append(event)

        return {
            "tick": self._tick,
            "new_folds": len(new_folds),
            "total_folds": len(self._fold_events),
        }

    def fabric_report(self) -> dict[str, Any]:
        dim_dist = defaultdict(int)
        fold_count = 0
        stress_count = 0
        tensions = []

        for cell in self._cells.values():
            dim_dist[cell.dimension] += 1
            if cell.folded:
                fold_count += 1
            if cell.is_stressed:
                stress_count += 1
            tensions.append(cell.tension)

        return {
            "tick": self._tick,
            "total_cells": len(self._cells),
            "dimension_distribution": dict(dim_dist),
            "folded_cells": fold_count,
            "stressed_cells": stress_count,
            "mean_tension": round(sum(tensions) / max(1, len(tensions)), 4),
            "max_tension": round(max(tensions), 4),
            "fold_events": len(self._fold_events),
        }


def demo() -> dict[str, Any]:
    sim = RealityFabricSim(width=8, height=8, seed=42)
    sim.init_fabric()
    for i in range(12):
        dim = ["primary", "secondary", "tertiary"][i % 3]
        sim.add_agent(f"agent-{i}", dimension=dim)

    for _ in range(40):
        sim.tick()

    return sim.fabric_report()


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
