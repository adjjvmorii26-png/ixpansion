"""Gravitational Analyzer — Models code dependencies as gravitational fields.

Each module has mass (size) and creates a gravitational field that pulls
on other modules. The system computes orbital mechanics and predicts
which modules will "collide" (merge) or "escape" (become independent).
"""
from __future__ import annotations
import hashlib
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GravitationalBody:
    def __init__(self, name: str, mass: float, x: float = 0, y: float = 0):
        self.name = name
        self.mass = mass
        self.x, self.y = x, y
        self.vx = self.vy = 0.0
        self.orbit_history: list[tuple[float, float]] = []

    def gravity_from(self, other: "GravitationalBody", G: float = 0.01) -> tuple[float, float]:
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.sqrt(dx*dx + dy*dy) + 0.1
        force = G * self.mass * other.mass / (dist * dist)
        return (force * dx / dist, force * dy / dist)

    def update(self, fx: float, fy: float, dt: float = 0.1):
        self.vx += fx / self.mass * dt
        self.vy += fy / self.mass * dt
        self.vx *= 0.99  # Damping
        self.vy *= 0.99
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.orbit_history.append((round(self.x, 2), round(self.y, 2)))

    def kinetic_energy(self) -> float:
        return 0.5 * self.mass * (self.vx**2 + self.vy**2)

    def to_dict(self) -> dict:
        return {
            "name": self.name, "mass": round(self.mass, 2),
            "position": (round(self.x, 2), round(self.y, 2)),
            "velocity": (round(self.vx, 4), round(self.vy, 4)),
            "kinetic_energy": round(self.kinetic_energy(), 4),
        }


class GravitationalSystem:
    def __init__(self, seed=42):
        self.seed = seed
        self.bodies: dict[str, GravitationalBody] = {}
        self.tick_count = 0
        self.G = 0.01

    def add_body(self, name: str, mass: float, x: float = 0, y: float = 0):
        self.bodies[name] = GravitationalBody(name, mass, x, y)

    def tick(self):
        self.tick_count += 1
        forces: dict[str, tuple[float, float]] = {n: (0.0, 0.0) for n in self.bodies}
        for a_name, a in self.bodies.items():
            for b_name, b in self.bodies.items():
                if a_name != b_name:
                    fx, fy = a.gravity_from(b, self.G)
                    forces[a_name] = (forces[a_name][0] + fx, forces[a_name][1] + fy)
        for name, (fx, fy) in forces.items():
            self.bodies[name].update(fx, fy)

    def simulate(self, ticks=20):
        for _ in range(ticks):
            self.tick()
        return {
            "ticks": ticks,
            "bodies": {n: b.to_dict() for n, b in self.bodies.items()},
            "total_kinetic_energy": round(sum(b.kinetic_energy() for b in self.bodies.values()), 4),
        }

    def find_collisions(self, threshold=0.5) -> list[dict]:
        collisions = []
        names = list(self.bodies.keys())
        for i, a in enumerate(names):
            for b in names[i+1:]:
                ba, bb = self.bodies[a], self.bodies[b]
                dist = math.sqrt((ba.x-bb.x)**2 + (ba.y-bb.y)**2)
                if dist < threshold:
                    collisions.append({"a": a, "b": b, "distance": round(dist, 4)})
        return collisions

    def report(self) -> dict:
        return {
            "system": "gravitational_system",
            "bodies": len(self.bodies),
            "ticks": self.tick_count,
            "collisions": self.find_collisions(),
            "body_details": {n: b.to_dict() for n, b in self.bodies.items()},
        }


def demo():
    system = GravitationalSystem(seed=42)
    import random
    rng = random.Random(42)
    dirs = {"api": ROOT / "api", "lab": ROOT / "lab" / "experiments", "bridges": ROOT / "bridges"}
    idx = 0
    for subsys, base in dirs.items():
        if base.exists():
            for py in list(base.glob("*.py"))[:8]:
                if not py.name.startswith("_"):
                    angle = rng.uniform(0, 2 * math.pi)
                    dist = rng.uniform(2, 8)
                    system.add_body(py.stem, py.stat().st_size / 1000,
                                    dist * math.cos(angle), dist * math.sin(angle))
                    idx += 1
    sim = system.simulate(ticks=30)
    return {"simulation": sim, "report": system.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
