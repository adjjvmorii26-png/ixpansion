#!/usr/bin/env python3
"""Dream Terrain Crystallizer — collective hallucinations become reality.

Bridges dream_sharing + pheromone_field + time_crystal to model how
agent dreams crystallize into persistent terrain. When multiple agents
dream the same archetype with enough density, and a time crystal
completes a full oscillation, the dream becomes permanent terrain.

This creates a feedback loop: terrain shaped by dreams influences
future exploration, which influences future dreams.
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
class DreamSeed:
    dreamer_id: str
    archetype: str
    intensity: float
    position: tuple[int, int]

    @property
    def weight(self) -> float:
        return max(0.0, min(1.0, self.intensity))


@dataclass
class CrystalFormation:
    formation_id: str
    archetype: str
    center: tuple[int, int]
    radius: int
    density: float = 0.0
    contributors: set[str] = field(default_factory=set)
    materialized: bool = False
    crystal_phase: int = 0
    crystal_period: int = 8

    @property
    def solidity(self) -> float:
        return min(1.0, self.density / 5.0)

    @property
    def is_crystal_complete(self) -> bool:
        return self.crystal_phase == 0 and self.density > 0

    def advance_crystal(self) -> bool:
        self.crystal_phase = (self.crystal_phase + 1) % self.crystal_period
        return self.crystal_phase == 0


@dataclass
class TerrainCell:
    terrain_type: str
    dream_source: str = ""
    crystallized_tick: int = 0
    decay_resistance: float = 0.5


@dataclass
class DreamTerrainCrystallizer:
    """A world where dreams and time crystals shape terrain."""
    width: int = 32
    height: int = 32
    materialization_threshold: float = 2.0
    dream_decay_rate: float = 0.03
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._terrain: dict[tuple[int, int], TerrainCell] = {}
        self._formations: dict[str, CrystalFormation] = {}
        self._dream_buffer: list[DreamSeed] = []
        self._tick = 0
        self._crystallization_log: list[dict[str, Any]] = []

    def receive_dream(self, seed: DreamSeed) -> None:
        """Receive a dream deposit from an agent."""
        self._dream_buffer.append(seed)

    def tick(self) -> dict[str, Any]:
        """Advance one world tick: accumulate, crystallize, decay."""
        self._tick += 1
        new_crystallizations: list[dict[str, Any]] = []

        # Process dream buffer into formations
        for seed in self._dream_buffer:
            key = f"{seed.archetype}:{seed.position[0]//4}:{seed.position[1]//4}"
            if key not in self._formations:
                self._formations[key] = CrystalFormation(
                    formation_id=hashlib.sha256(key.encode()).hexdigest()[:12],
                    archetype=seed.archetype,
                    center=seed.position,
                    radius=4,
                    crystal_period=self._rng.randint(6, 12),
                )
            form = self._formations[key]
            form.density += seed.weight
            form.contributors.add(seed.dreamer_id)
        self._dream_buffer.clear()

        # Advance crystal oscillations and check for materialization
        for form_id, form in list(self._formations.items()):
            completed = form.advance_crystal()
            if form.density >= self.materialization_threshold and completed:
                if not form.materialized:
                    form.materialized = True
                    self._materialize(form)
                    event = {
                        "tick": self._tick,
                        "archetype": form.archetype,
                        "center": form.center,
                        "contributors": len(form.contributors),
                        "density": round(form.density, 3),
                    }
                    new_crystallizations.append(event)
                    self._crystallization_log.append(event)

        # Decay formations
        for form in self._formations.values():
            if not form.materialized:
                form.density = max(0.0, form.density - self.dream_decay_rate)

        return {
            "tick": self._tick,
            "new_crystallizations": new_crystallizations,
            "active_formations": sum(1 for f in self._formations.values() if not f.materialized),
            "materialized_formations": sum(1 for f in self._formations.values() if f.materialized),
            "terrain_cells": len(self._terrain),
        }

    def _materialize(self, formation: CrystalFormation) -> None:
        cx, cy = formation.center
        for dx in range(-formation.radius, formation.radius + 1):
            for dy in range(-formation.radius, formation.radius + 1):
                if dx * dx + dy * dy <= formation.radius ** 2:
                    pos = (
                        (cx + dx) % self.width,
                        (cy + dy) % self.height,
                    )
                    self._terrain[pos] = TerrainCell(
                        terrain_type=formation.archetype,
                        dream_source=formation.formation_id,
                        crystallized_tick=self._tick,
                        decay_resistance=min(1.0, formation.density / 10.0),
                    )

    def query_terrain(self, x: int, y: int) -> dict[str, Any]:
        pos = (x % self.width, y % self.height)
        cell = self._terrain.get(pos)
        if cell:
            return {
                "position": list(pos),
                "terrain": cell.terrain_type,
                "source": cell.dream_source,
                "age": self._tick - cell.crystallized_tick,
                "decay_resistance": round(cell.decay_resistance, 3),
            }
        return {"position": list(pos), "terrain": "void"}

    def summary(self) -> dict[str, Any]:
        terrain_types: dict[str, int] = defaultdict(int)
        for cell in self._terrain.values():
            terrain_types[cell.terrain_type] += 1
        return {
            "tick": self._tick,
            "total_terrain": len(self._terrain),
            "terrain_distribution": dict(terrain_types),
            "total_crystallizations": len(self._crystallization_log),
            "formation_count": len(self._formations),
        }


def demo() -> dict[str, Any]:
    world = DreamTerrainCrystallizer(seed=42, materialization_threshold=1.5)

    # 5 agents dream about 3 archetypes, concentrating near grid centers
    archetypes = ["forest", "ocean", "crystal"]
    centers = [(8, 8), (24, 24), (16, 16)]
    for tick in range(30):
        for agent in range(5):
            arch_idx = (tick + agent) % len(archetypes)
            arch = archetypes[arch_idx]
            cx, cy = centers[arch_idx]
            # Dream near the archetype center with some jitter
            pos = (
                (cx + random.Random(tick * 7 + agent).randint(-3, 3)) % 32,
                (cy + random.Random(tick * 11 + agent).randint(-3, 3)) % 32,
            )
            world.receive_dream(DreamSeed(
                dreamer_id=f"agent-{agent}",
                archetype=arch,
                intensity=0.6 + random.Random(tick * 10 + agent).random() * 0.4,
                position=pos,
            ))
        world.tick()

    return world.summary()


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
