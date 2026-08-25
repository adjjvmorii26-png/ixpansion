#!/usr/bin/env python3
"""Panopticon Ecology — environment watches and reshapes itself around visitors.

Bridges panopticon + terrain + species affinity to create a world where
the environment is alive and responsive. Cells track who visits them
and reshape their terrain based on accumulated affinities.

Frequent sentinel visits → fortified terrain. Frequent wanderer visits → trail networks.
Hostile species → toxic/barren terrain. The world literally becomes what its
inhabitants make it through their footprints.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


TERRAIN_RESPONSES = {
    "sentinel": {"positive": "fortified", "neutral": "plains", "negative": "barricade"},
    "architect": {"positive": "quarry", "neutral": "plains", "negative": "rubble"},
    "wanderer": {"positive": "trail", "neutral": "plains", "negative": "thicket"},
}

TERRAIN_DESCRIPTIONS = {
    "fortified": "Walls and watchtowers emerge from the ground",
    "quarry": "Raw stone surfaces, ready for building",
    "trail": "Smooth paths wind between natural features",
    "barricade": "Impassable tangles block all movement",
    "rubble": "Broken stone creates difficult terrain",
    "thicket": "Dense undergrowth obscures all paths",
    "plains": "Open, neutral ground",
    "barren": "Lifeless soil, nothing grows",
    "toxic": "Corrosive atmosphere, dangerous to enter",
}


@dataclass
class LivingCell:
    position: tuple[int, int]
    terrain: str = "plains"
    species_affinity: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    total_visits: int = 0
    visit_history: list[str] = field(default_factory=list)
    mood: str = "indifferent"

    @property
    def dominant_species(self) -> str:
        if not self.species_affinity:
            return "none"
        return max(self.species_affinity, key=self.species_affinity.get)

    @property
    def total_affinity(self) -> float:
        return sum(abs(v) for v in self.species_affinity.values())

    def receive_visit(self, agent_id: str, species: str) -> str:
        self.total_visits += 1
        self.visit_history.append(species)
        if len(self.visit_history) > 20:
            self.visit_history = self.visit_history[-20:]
        self.species_affinity[species] += 0.1
        return self._reshape()

    def _reshape(self) -> str:
        if not self.species_affinity:
            return self.terrain

        dominant = self.dominant_species
        score = self.species_affinity[dominant]

        if score >= 1.5:
            self.mood = "nurturing"
            self.terrain = TERRAIN_RESPONSES.get(dominant, {}).get("positive", "fertile")
        elif score <= -0.5:
            self.mood = "hostile"
            self.terrain = TERRAIN_RESPONSES.get(dominant, {}).get("negative", "barren")
        else:
            self.mood = "indifferent"
            self.terrain = "plains"

        return self.terrain


@dataclass
class PanopticonEcology:
    width: int = 12
    height: int = 12
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._cells: dict[tuple[int, int], LivingCell] = {}
        self._agents: dict[str, dict[str, str]] = {}
        self._tick = 0
        self._terrain_shifts: list[dict[str, Any]] = []

    def init_cells(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                self._cells[(x, y)] = LivingCell(position=(x, y))

    def add_agent(self, agent_id: str, species: str,
                  position: tuple[int, int] | None = None) -> None:
        if position is None:
            position = (self._rng.randint(0, self.width - 1),
                       self._rng.randint(0, self.height - 1))
        self._agents[agent_id] = {"species": species, "position": f"{position[0]},{position[1]}"}

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        shifts: list[dict[str, Any]] = []

        for agent_id, agent_data in self._agents.items():
            pos_str = agent_data["position"]
            x, y = int(pos_str.split(",")[0]), int(pos_str.split(",")[1])

            # Agent wanders
            dx = self._rng.randint(-1, 1)
            dy = self._rng.randint(-1, 1)
            new_x = (x + dx) % self.width
            new_y = (y + dy) % self.height
            agent_data["position"] = f"{new_x},{new_y}"

            cell = self._cells.get((new_x, new_y))
            if cell:
                old_terrain = cell.terrain
                cell.receive_visit(agent_id, agent_data["species"])
                if cell.terrain != old_terrain:
                    shifts.append({
                        "tick": self._tick,
                        "position": [new_x, new_y],
                        "old_terrain": old_terrain,
                        "new_terrain": cell.terrain,
                        "agent": agent_id,
                        "species": agent_data["species"],
                    })

        self._terrain_shifts.extend(shifts)
        return {"tick": self._tick, "shifts": len(shifts)}

    def ecology_report(self) -> dict[str, Any]:
        terrain_dist: dict[str, int] = defaultdict(int)
        mood_dist: dict[str, int] = defaultdict(int)
        for cell in self._cells.values():
            terrain_dist[cell.terrain] += 1
            mood_dist[cell.mood] += 1

        most_active = max(self._cells.values(), key=lambda c: c.total_visits) if self._cells else None
        return {
            "tick": self._tick,
            "total_cells": len(self._cells),
            "terrain_distribution": dict(terrain_dist),
            "mood_distribution": dict(mood_dist),
            "total_shifts": len(self._terrain_shifts),
            "most_active_cell": {
                "position": list(most_active.position),
                "visits": most_active.total_visits,
                "terrain": most_active.terrain,
            } if most_active else None,
        }


def demo() -> dict[str, Any]:
    eco = PanopticonEcology(width=8, height=8, seed=42)
    eco.init_cells()
    species = ["sentinel", "architect", "wanderer"]
    for i in range(12):
        eco.add_agent(f"agent-{i}", species[i % 3])

    for _ in range(25):
        eco.tick()

    return eco.ecology_report()


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
