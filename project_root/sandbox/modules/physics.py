import math
from typing import Any


class PhysicsEngine:
    """Lightweight 2D physics: gravity, collision, friction."""

    GRAVITY = -9.8

    def apply_gravity(self, velocity: list[float], dt: float = 1.0) -> list[float]:
        return [velocity[0], velocity[1] + self.GRAVITY * dt]

    def check_collision(self, a_pos: list[float], a_radius: float,
                        b_pos: list[float], b_radius: float) -> bool:
        dx, dy = a_pos[0] - b_pos[0], a_pos[1] - b_pos[1]
        dist = math.hypot(dx, dy)
        return dist <= (a_radius + b_radius)

    def apply_friction(self, velocity: list[float], coefficient: float = 0.98) -> list[float]:
        return [velocity[0] * coefficient, velocity[1] * coefficient]
