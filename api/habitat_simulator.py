"""Habitat Simulator — creates evolving environments for agent populations.

Agents live in simulated habitats with resources, threats, seasons, and
terrain. The habitat evolves independently — rainfall changes, new species
appear, climate shifts. Agents must adapt or face extinction. The best
adaptations become permanent features of the ecosystem.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SEASONS = ["spring", "summer", "autumn", "winter"]
TERRAIN_TYPES = ["forest", "desert", "ocean", "mountain", "swamp", "tundra"]


class HabitatCell:
    def __init__(self, x: int, y: int, terrain: str = None):
        self.x = x
        self.y = y
        self.terrain = terrain or random.choice(TERRAIN_TYPES)
        self.resources = random.uniform(0.1, 1.0)
        self.temperature = random.uniform(-10, 40)
        self.moisture = random.uniform(0.0, 1.0)
        self.occupants: List[str] = []

    def tick(self, season: str):
        season_mods = {
            "spring": {"temp": 5, "moisture": 0.1, "resources": 0.05},
            "summer": {"temp": 10, "moisture": -0.1, "resources": -0.02},
            "autumn": {"temp": -5, "moisture": 0.05, "resources": -0.05},
            "winter": {"temp": -15, "moisture": -0.05, "resources": -0.1},
        }
        mod = season_mods.get(season, {})
        self.temperature += mod.get("temp", 0) + random.uniform(-2, 2)
        self.moisture = max(0, min(1, self.moisture + mod.get("moisture", 0)))
        self.resources = max(0, min(1, self.resources + mod.get("resources", 0)))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": [self.x, self.y],
            "terrain": self.terrain,
            "resources": round(self.resources, 3),
            "temperature": round(self.temperature, 1),
            "moisture": round(self.moisture, 3),
            "occupants": len(self.occupants),
        }


class HabitatSimulator:
    def __init__(self, width: int = 5, height: int = 5):
        self.grid: Dict[tuple, HabitatCell] = {}
        self.current_season = "spring"
        self.tick_count = 0
        self.populations: Dict[str, Dict[str, Any]] = {}
        self.history: List[Dict[str, Any]] = []
        for x in range(width):
            for y in range(height):
                self.grid[(x, y)] = HabitatCell(x, y)

    def tick(self) -> Dict[str, Any]:
        self.tick_count += 1
        if self.tick_count % 4 == 0:
            season_idx = (self.tick_count // 4) % 4
            self.current_season = SEASONS[season_idx]
        for cell in self.grid.values():
            cell.tick(self.current_season)
        total_resources = sum(c.resources for c in self.grid.values())
        avg_temp = sum(c.temperature for c in self.grid.values()) / len(self.grid)
        snapshot = {
            "tick": self.tick_count,
            "season": self.current_season,
            "total_resources": round(total_resources, 2),
            "avg_temperature": round(avg_temp, 1),
            "population_count": len(self.populations),
        }
        self.history.append(snapshot)
        return snapshot

    def introduce_species(self, species_id: str, count: int = 5) -> Dict[str, Any]:
        cells = list(self.grid.values())
        placed = 0
        for _ in range(min(count, len(cells))):
            cell = random.choice(cells)
            cell.occupants.append(species_id)
            placed += 1
        self.populations[species_id] = {"count": placed, "born_tick": self.tick_count}
        return {"species": species_id, "placed": placed}

    def cell_map(self) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self.grid.values()]

    def species_report(self) -> Dict[str, Any]:
        species_counts: Dict[str, int] = {}
        for cell in self.grid.values():
            for occupant in cell.occupants:
                species_counts[occupant] = species_counts.get(occupant, 0) + 1
        return species_counts

    def habitat_stats(self) -> Dict[str, Any]:
        return {
            "grid_size": len(self.grid),
            "tick": self.tick_count,
            "season": self.current_season,
            "species": len(self.populations),
            "total_resources": round(sum(c.resources for c in self.grid.values()), 2),
        }


_simulator = HabitatSimulator(5, 5)


def habitat_simulator_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "tick":
        return _simulator.tick()
    elif action == "introduce":
        return _simulator.introduce_species(
            payload.get("species", f"species_{random.randint(100,999)}"),
            payload.get("count", 5),
        )
    elif action == "map":
        return {"cells": _simulator.cell_map()}
    elif action == "species":
        return {"species": _simulator.species_report()}
    return {"status": "active", **_simulator.habitat_stats()}


handler = habitat_simulator_handler
