"""Stigmergic pheromone field for emergent coordination.

Agents deposit chemical-like signals into a spatial grid. Deposits
evaporate exponentially each tick. Other agents sensing high concentrations
are probabilistically attracted toward them — creating self-organizing
trail networks without any direct agent-to-agent messaging.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Deposit:
    intensity: float  # 0.0 to 1.0
    species: str
    tick_placed: int


class PheromoneField:
    """2D spatial pheromone grid with species-specific signaling."""

    def __init__(self, width: int = 32, height: int = 32) -> None:
        self.width = width
        self.height = height
        self._grid: dict[tuple[int, int], list[Deposit]] = defaultdict(list)
        self._tick = 0

    def deposit(self, x: int, y: int, species: str, intensity: float = 1.0) -> None:
        """Place a pheromone deposit at (x, y)."""
        clamped_x = max(0, min(x, self.width - 1))
        clamped_y = max(0, min(y, self.height - 1))
        self._grid[(clamped_x, clamped_y)].append(
            Deposit(intensity=max(0.0, min(1.0, intensity)), species=species, tick_placed=self._tick)
        )

    def sense(self, x: int, y: int, species: str, radius: int = 2) -> float:
        """Measure total same-species pheromone concentration near (x, y)."""
        total = 0.0
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                cell_key = (
                    max(0, min(x + dx, self.width - 1)),
                    max(0, min(y + dy, self.height - 1)),
                )
                for dep in self._grid.get(cell_key, []):
                    if dep.species == species:
                        dist = math.hypot(dx, dy)
                        falloff = math.exp(-dist / max(radius, 1))
                        total += dep.intensity * falloff
        return round(total, 6)

    def evaporate(self, rate: float = 0.05) -> None:
        """Decay all deposits by the evaporation rate."""
        self._tick += 1
        expired_keys = []
        for key, deposits in self._grid.items():
            surviving = []
            for dep in deposits:
                new_intensity = dep.intensity * (1.0 - rate)
                if new_intensity > 0.01:
                    dep.intensity = round(new_intensity, 6)
                    surviving.append(dep)
            if surviving:
                self._grid[key] = surviving
            else:
                expired_keys.append(key)
        for key in expired_keys:
            del self._grid[key]

    def attract_to(self, x: int, y: int, species: str, sensitivity: float = 0.5) -> tuple[int, int] | None:
        """Find strongest nearby concentration and return gradient step.
        Returns None if no significant signal found."""
        best_intensity = 0.0
        best_pos: tuple[int, int] | None = None

        for dx in range(-3, 4):
            for dy in range(-3, 4):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                local = self.sense(nx, ny, species, radius=1)
                if local > best_intensity and local >= sensitivity:
                    best_intensity = local
                    best_pos = (nx, ny)

        if best_pos is None:
            return None
        return best_pos

    @property
    def density_map(self) -> dict[str, float]:
        """Aggregate intensity per species across the entire field."""
        totals: dict[str, float] = defaultdict(float)
        for deposits in self._grid.values():
            for dep in deposits:
                totals[dep.species] += dep.intensity
        return dict(totals)

    @property
    def tick(self) -> int:
        return self._tick
