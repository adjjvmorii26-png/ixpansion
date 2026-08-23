import math
from typing import Any


class PhysicsEngine:
    """Vector-based 2D physics with collision detection."""

    GRAVITY: float = -9.81
    DRAG: float = 0.995

    def integrate(self, position: list[float], velocity: list[float], dt: float = 1.0) -> tuple[list[float], list[float]]:
        new_vel = [velocity[0] * self.DRAG, velocity[1] + self.GRAVITY * dt]
        new_pos = [position[0] + new_vel[0] * dt, position[1] + new_vel[1] * dt]
        return new_pos, new_vel

    @staticmethod
    def collides(a_pos: list[float], a_r: float, b_pos: list[float], b_r: float) -> bool:
        dist = math.hypot(a_pos[0] - b_pos[0], a_pos[1] - b_pos[1])
        return dist <= a_r + b_r
