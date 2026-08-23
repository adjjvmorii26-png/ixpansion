"""Global world state container."""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorldState:
    tick: int = 0
    entities: dict[str, dict[str, Any]] = field(default_factory=dict)
    terrain: dict[tuple[int, int], str] = field(default_factory=dict)
    global_constants: dict[str, float] = field(default_factory=lambda: {
        "gravity": -9.81,
        "time_flow": 1.0,
        "chaos_level": 0.5,
    })

    def snapshot(self) -> dict[str, Any]:
        return copy.deepcopy({
            "tick": self.tick,
            "entity_count": len(self.entities),
            "terrain_cells": len(self.terrain),
            "constants": dict(self.global_constants),
        })

    def advance(self) -> int:
        self.tick += 1
        return self.tick

    def place_entity(self, entity_id: str, data: dict[str, Any]) -> None:
        self.entities[entity_id] = data

    def remove_entity(self, entity_id: str) -> bool:
        return self.entities.pop(entity_id, None) is not None

    def set_terrain(self, pos: tuple[int, int], kind: str) -> None:
        self.terrain[pos] = kind

    @property
    def entity_ids(self) -> list[str]:
        return list(self.entities.keys())
