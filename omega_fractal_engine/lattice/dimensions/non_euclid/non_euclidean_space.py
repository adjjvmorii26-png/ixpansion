"""Impossible geometry — distances and adjacencies violate expectations."""
from __future__ import annotations

import math
import random
from typing import Any


class NonEuclideanSpace:
    """Space where parallel lines meet, angles sum ≠ 180°, and
    walking in a straight line may return you to your origin."""

    def __init__(self, dims: int = 3, warp_factor: float = 0.3) -> None:
        self.dims = dims
        self.warp = warp_factor
        self._warps: dict[tuple[int, ...], tuple[int, ...]] = {}

    def distance(self, a: tuple[float, ...], b: tuple[float, ...]) -> float:
        base = math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
        # Distance is non-symmetric: d(a,b) ≠ d(b,a) sometimes
        direction_bias = 1.0 + (self.warp * math.sin(sum(a) - sum(b)))
        return max(0.01, base * abs(direction_bias))

    def adjacency(self, pos: tuple[int, ...]) -> list[tuple[int, ...]]:
        neighbors = []
        for d in range(self.dims):
            for delta in (-1, 0, 1):  # Note: includes "staying" as a neighbor
                if delta == 0 and random.random() > self.warp:
                    continue  # Sometimes you can't stay still
                new = list(pos)
                new[d] += delta
                # Random teleport chance
                if random.random() < self.warp * 0.1:
                    new[d] += random.randint(-3, 3)
                neighbors.append(tuple(new))
        return neighbors

    def add_warp(self, src: tuple[int, ...], dst: tuple[int, ...]) -> None:
        """Create a permanent spatial warp between two cells."""
        self._warps[src] = dst

    def resolve(self, pos: tuple[int, ...]) -> tuple[int, ...]:
        return self._warps.get(pos, pos)

    @property
    def name(self) -> str:
        return f"non_euclid_{self.dims}d_warp{self.warp}"
