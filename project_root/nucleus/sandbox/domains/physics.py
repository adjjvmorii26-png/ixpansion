"""Physics domain — spatial rules and motion."""
from __future__ import annotations

import math
from typing import Any


class PhysicsDomain:
    GRAVITY = -9.81

    def integrate(self, pos: tuple[float, float], vel: tuple[float, float],
                  dt: float = 1.0) -> tuple[tuple[float, float], tuple[float, float]]:
        nv = (vel[0], vel[1] + self.GRAVITY * dt)
        np_ = (pos[0] + nv[0] * dt, pos[1] + nv[1] * dt)
        return np_, nv

    def distance(self, a: tuple[float, ...], b: tuple[float, ...]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def within_range(self, a: tuple[float, float], b: tuple[float, float],
                     radius: float) -> bool:
        return self.distance(a, b) <= radius
