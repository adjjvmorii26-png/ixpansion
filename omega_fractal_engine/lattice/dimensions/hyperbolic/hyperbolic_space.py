"""Curved infinite space — exponentially expanding neighborhoods."""
from __future__ import annotations

import math
from typing import Any


class HyperbolicSpace:
    """Space with constant negative curvature — the number of neighbors
    grows exponentially with radius, creating effectively infinite room."""

    def __init__(self, curvature: float = -1.0, max_radius: int = 20) -> None:
        self.k = curvature  # Must be negative
        self.max_r = max_radius

    def distance(self, a: tuple[float, ...], b: tuple[float, ...]) -> float:
        """Hyperbolic distance formula (simplified Poincaré disk model)."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a_sq = sum(x ** 2 for x in a)
        norm_b_sq = sum(x ** 2 for x in b)

        denom = 1 - 2 * dot + norm_a_sq * norm_b_sq
        if denom <= 0:
            denom = 0.001

        arg = min(1.0, 1 + 2 * (sum((x - y) ** 2 for x, y in zip(a, b))) / denom)
        return math.acosh(max(1.0, arg)) / math.sqrt(abs(self.k))

    def circumference_at_radius(self, r: float) -> float:
        """Circumference of a circle at hyperbolic radius r — grows exponentially."""
        return 2 * math.pi * math.sinh(math.sqrt(abs(self.k)) * r) / math.sqrt(abs(self.k))

    def area_at_radius(self, r: float) -> float:
        return 4 * math.pi * math.sinh(math.sqrt(abs(self.k)) * r / 2) ** 2 / abs(self.k)

    def neighbors_within(self, center: tuple[float, ...], r: int) -> int:
        """Approximate number of lattice points within hyperbolic radius."""
        area = self.area_at_radius(r)
        cell_area = 4 * math.pi / (abs(self.k) * (abs(self.k) + 1))  # Approximate
        return max(1, int(area / cell_area))

    @property
    def name(self) -> str:
        return f"hyperbolic_k{self.k}_r{self.max_r}"

    @property
    def is_infinite(self) -> bool:
        """True because circumference diverges."""
        return True
