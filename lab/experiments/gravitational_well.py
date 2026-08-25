from __future__ import annotations
"""Gravitational Well — module attraction/repulsion dynamics.

Modules have "mass" (complexity) and exert gravitational force on each
other. Related modules attract; conflicting modules repel. Orbits form
naturally around high-mass hubs. The system models N-body dynamics with
friction and energy conservation.
"""
import math
import random
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

G = 6.674  # Gravitational constant (scaled for simulation)
FRICTION = 0.995
DT = 0.05
MAX_SPEED = 5.0

@dataclass
class CelestialBody:
    name: str
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    mass: float = 1.0
    radius: float = 2.0
    fixed: bool = False
    trail: List[Tuple[float, float]] = field(default_factory=list)
    orbit_count: int = 0
    energy: float = 0.0

@dataclass
class ForceVector:
    fx: float
    fy: float
    magnitude: float
    source: str

@dataclass
class OrbitalSystem:
    bodies: List[str]
    center: str
    avg_radius: float
    avg_speed: float
    stability: float

class GravitationalWell:
    def __init__(self, width: float = 200.0, height: float = 200.0):
        self.width = width
        self.height = height
        self.bodies: Dict[str, CelestialBody] = {}
        self.force_log: List[Dict] = []
        self.orbits: List[OrbitalSystem] = []
        self.tick = 0
        self.energy_history: List[float] = []

    def add_body(self, name: str, x: float, y: float, mass: float = 1.0,
                 fixed: bool = False) -> CelestialBody:
        body = CelestialBody(
            name=name, x=x, y=y, mass=mass,
            radius=max(1.5, math.sqrt(mass) * 1.5),
            fixed=fixed,
        )
        self.bodies[name] = body
        return body

    def _gravitational_force(self, a: CelestialBody, b: CelestialBody) -> ForceVector:
        dx = b.x - a.x
        dy = b.y - a.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.5:
            dist = 0.5
        force_magnitude = G * a.mass * b.mass / (dist * dist)
        fx = force_magnitude * dx / dist
        fy = force_magnitude * dy / dist
        return ForceVector(fx=fx, fy=fy, magnitude=force_magnitude, source=b.name)

    def _total_energy(self) -> float:
        energy = 0.0
        bodies = list(self.bodies.values())
        for b in bodies:
            energy += 0.5 * b.mass * (b.vx ** 2 + b.vy ** 2)
        for i, a in enumerate(bodies):
            for b in bodies[i + 1:]:
                dx = b.x - a.x
                dy = b.y - a.y
                dist = math.sqrt(dx * dx + dy * dy) + 0.1
                energy -= G * a.mass * b.mass / dist
        return energy

    def step(self):
        self.tick += 1
        bodies = list(self.bodies.values())
        forces: Dict[str, Tuple[float, float]] = {b.name: (0.0, 0.0) for b in bodies}

        for i, a in enumerate(bodies):
            for b in bodies[i + 1:]:
                fv = self._gravitational_force(a, b)
                forces[a.name] = (forces[a.name][0] + fv.fx, forces[a.name][1] + fv.fy)
                forces[b.name] = (forces[b.name][0] - fv.fx, forces[b.name][1] - fv.fy)

        for body in bodies:
            if body.fixed:
                continue
            fx, fy = forces[body.name]
            body.vx += fx / body.mass * DT
            body.vy += fy / body.mass * DT
            speed = math.sqrt(body.vx ** 2 + body.vy ** 2)
            if speed > MAX_SPEED:
                body.vx *= MAX_SPEED / speed
                body.vy *= MAX_SPEED / speed
            body.vx *= FRICTION
            body.vy *= FRICTION
            body.x += body.vx * DT
            body.y += body.vy * DT
            body.x = body.x % self.width
            body.y = body.y % self.height
            body.trail.append((round(body.x, 2), round(body.y, 2)))
            if len(body.trail) > 50:
                body.trail.pop(0)

        self.energy_history.append(self._total_energy())

    def detect_orbits(self, min_bodies: int = 2) -> List[OrbitalSystem]:
        orbits = []
        bodies = list(self.bodies.values())
        for center in bodies:
            orbiters = []
            for other in bodies:
                if other.name == center.name:
                    continue
                dx = other.x - center.x
                dy = other.y - center.y
                dist = math.sqrt(dx * dx + dy * dy)
                speed = math.sqrt(other.vx ** 2 + other.vy ** 2)
                orbital_speed = math.sqrt(G * center.mass / max(dist, 0.1))
                if abs(speed - orbital_speed) < orbital_speed * 0.5:
                    orbiters.append(other.name)
            if len(orbiters) >= min_bodies:
                radii = [math.sqrt((self.bodies[n].x - center.x)**2 +
                                   (self.bodies[n].y - center.y)**2)
                         for n in orbiters]
                speeds = [math.sqrt(self.bodies[n].vx**2 + self.bodies[n].vy**2)
                          for n in orbiters]
                orbits.append(OrbitalSystem(
                    bodies=orbiters, center=center.name,
                    avg_radius=sum(radii) / len(radii),
                    avg_speed=sum(speeds) / len(speeds),
                    stability=1.0 - abs(self.energy_history[-1] - self.energy_history[0]) /
                    max(abs(self.energy_history[0]), 1) if self.energy_history else 0,
                ))
        self.orbits = orbits
        return orbits

    def state(self) -> Dict:
        return {
            "tick": self.tick,
            "bodies": len(self.bodies),
            "energy": round(self.energy_history[-1], 4) if self.energy_history else 0,
            "orbits_detected": len(self.orbits),
            "positions": {
                name: (round(b.x, 2), round(b.y, 2))
                for name, b in self.bodies.items()
            },
        }


def demo():
    gw = GravitationalWell(width=100, height=100)
    print("=== Gravitational Well ===")
    gw.add_body("nucleus", 50, 50, mass=50.0, fixed=True)
    gw.add_body("agent_alpha", 30, 50, mass=2.0)
    gw.add_body("agent_beta", 70, 50, mass=3.0)
    gw.add_body("agent_gamma", 50, 30, mass=1.5)
    gw.add_body("observer", 50, 80, mass=1.0)
    gw.add_body("paradox", 20, 20, mass=4.0)

    for _ in range(100):
        gw.step()

    orbits = gw.detect_orbits()
    print(f"  Simulation ticks: {gw.tick}")
    print(f"  Total energy: {gw.energy_history[-1]:.4f}")
    print(f"  Energy drift: {abs(gw.energy_history[-1] - gw.energy_history[0]):.6f}")
    print(f"  Orbits detected: {len(orbits)}")

    for o in orbits:
        print(f"    Center: {o.center}, orbiters: {o.bodies}, "
              f"avg_radius: {o.avg_radius:.1f}, stability: {o.stability:.3f}")

    state = gw.state()
    for name, pos in state["positions"].items():
        body = gw.bodies[name]
        print(f"  {name}: pos={pos}, vel=({body.vx:.3f}, {body.vy:.3f}), "
              f"mass={body.mass}")

    return state


if __name__ == "__main__":
    demo()
