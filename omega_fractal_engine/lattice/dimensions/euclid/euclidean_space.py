"""Standard Euclidean geometry — flat space with familiar rules."""
from __future__ import annotations

import math
from typing import Any


class EuclideanSpace:
    def __init__(self, dimensions: int = 3) -> None:
        self.dims = dimensions

    def distance(self, a: tuple[float, ...], b: tuple[float, ...]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def adjacency(self, pos: tuple[int, ...]) -> list[tuple[int, ...]]:
        neighbors = []
        for d in range(self.dims):
            for delta in (-1, 1):
                new = list(pos)
                new[d] += delta
                neighbors.append(tuple(new))
        return neighbors

    @property
    def name(self) -> str:
        return f"euclid_{self.dims}d"
