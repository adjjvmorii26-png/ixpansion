#!/usr/bin/env python3
"""Consensus Reality Simulator — model how shared truth emerges from individual perception.

Bridges consensus_reality + observation + truth_collapse to simulate
how agents with biased observations collectively converge on (or diverge
from) objective reality.

Each agent observes a cell with personal bias. When enough agents agree,
the observation "collapses" into consensus truth. When they disagree,
the cell remains ambiguous. Over time, this creates a landscape of
settled and unsettled territories — a map of collective knowledge
vs. collective confusion.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Cell:
    position: tuple[int, int]
    ground_truth: str
    observations: dict[str, str] = field(default_factory=dict)
    confidence: dict[str, float] = field(default_factory=dict)
    consolidated: bool = False
    consolidated_truth: str | None = None

    @property
    def observation_count(self) -> int:
        return len(self.observations)

    def try_consolidate(self, threshold: float = 0.6) -> str | None:
        if not self.observations or self.consolidated:
            return None
        counts = Counter(self.observations.values())
        total = sum(counts.values())
        for truth, count in counts.most_common():
            if count / total >= threshold:
                self.consolidated = True
                self.consolidated_truth = truth
                return truth
        return None


@dataclass
class RealityAgent:
    agent_id: str
    species: str
    bias: float  # -1 to 1, how much observations deviate from truth
    position: tuple[float, float]
    observations_made: int = 0
    lies_told: int = 0

    def observe(self, cell: Cell) -> str:
        """Observe a cell with personal bias."""
        truth = cell.ground_truth
        if abs(self.bias) > 0.3 and random.random() < abs(self.bias):
            # Biased observation: sometimes report differently
            alternatives = ["forest", "void", "water", "crystal", "rock", "fire"]
            observed = random.choice([a for a in alternatives if a != truth])
            self.lies_told += 1
        else:
            observed = truth
        self.observations_made += 1
        cell.observations[self.agent_id] = observed
        cell.confidence[self.agent_id] = 0.7 + abs(self.bias) * 0.3
        return observed


@dataclass
class ConsensusRealitySimulator:
    width: int = 12
    height: int = 12
    consolidation_threshold: float = 0.6
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._world: dict[tuple[int, int], Cell] = {}
        self._agents: list[RealityAgent] = []
        self._tick = 0
        self._consolidation_events: list[dict[str, Any]] = []

    def init_world(self, terrain_map: dict[tuple[int, int], str] | None = None) -> None:
        truths = ["forest", "void", "water", "crystal", "rock", "fire"]
        for y in range(self.height):
            for x in range(self.width):
                if terrain_map and (x, y) in terrain_map:
                    truth = terrain_map[(x, y)]
                else:
                    # Create clusters
                    cx, cy = x // 4, y // 4
                    truth = truths[(cx + cy) % len(truths)]
                self._world[(x, y)] = Cell(position=(x, y), ground_truth=truth)

    def add_agents(self, count: int = 10) -> None:
        for i in range(count):
            bias = self._rng.uniform(-0.5, 0.5)
            species = ["sentinel", "architect", "wanderer"][i % 3]
            self._agents.append(RealityAgent(
                agent_id=f"agent-{i}",
                species=species,
                bias=bias,
                position=(self._rng.uniform(0, self.width), self._rng.uniform(0, self.height)),
            ))

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        new_consolidations = 0

        # Agents observe random nearby cells
        for agent in self._agents:
            # Pick a random cell near the agent
            cx = int(agent.position[0]) % self.width
            cy = int(agent.position[1]) % self.height
            dx = self._rng.randint(-1, 1)
            dy = self._rng.randint(-1, 1)
            target = ((cx + dx) % self.width, (cy + dy) % self.height)
            cell = self._world.get(target)
            if cell:
                agent.observe(cell)

        # Try to consolidate unsettled cells
        for cell in self._world.values():
            if not cell.consolidated and cell.observation_count >= 2:
                result = cell.try_consolidate(self.consolidation_threshold)
                if result:
                    new_consolidations += 1
                    self._consolidation_events.append({
                        "tick": self._tick,
                        "position": list(cell.position),
                        "truth": result,
                        "correct": result == cell.ground_truth,
                        "observations": cell.observation_count,
                    })

        return {
            "tick": self._tick,
            "new_consolidations": new_consolidations,
            "total_consolidated": sum(1 for c in self._world.values() if c.consolidated),
        }

    def accuracy_report(self) -> dict[str, Any]:
        correct = 0
        total = 0
        for cell in self._world.values():
            if cell.consolidated:
                total += 1
                if cell.consolidated_truth == cell.ground_truth:
                    correct += 1

        agent_liars = sum(1 for a in self._agents if a.lies_told > a.observations_made * 0.3)
        return {
            "accuracy": round(correct / max(1, total), 4),
            "consolidated": total,
            "total_cells": len(self._world),
            "settled_ratio": round(total / max(1, len(self._world)), 4),
            "deceptive_agents": agent_liars,
            "total_observations": sum(a.observations_made for a in self._agents),
        }


def demo() -> dict[str, Any]:
    sim = ConsensusRealitySimulator(width=8, height=8, seed=42)
    sim.init_world()
    sim.add_agents(8)

    for _ in range(30):
        sim.tick()

    return {
        "accuracy_report": sim.accuracy_report(),
        "consolidation_events": len(sim._consolidation_events),
        "sample_events": sim._consolidation_events[:5],
    }


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
