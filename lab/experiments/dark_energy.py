from __future__ import annotations
"""Dark Energy — the expansion force that drives system growth.

Models the mysterious force that causes the codebase to expand. Dark
energy density determines the rate of expansion. As the system grows,
dark energy can accelerate or decelerate growth, creating interesting
dynamics between gravity (module attraction) and expansion.
"""
import math
import random
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class CosmicBody:
    name: str
    mass: float
    position: float
    velocity: float = 0.0
    dark_energy_susceptibility: float = 1.0

class DarkEnergyEngine:
    def __init__(self, dark_energy_density: float = 0.7, scale_factor: float = 1.0):
        self.dark_energy_density = dark_energy_density
        self.scale_factor = scale_factor
        self.bodies: Dict[str, CosmicBody] = {}
        self.expansion_history: List[Dict] = []
        self.tick = 0

    def add_body(self, name: str, mass: float, position: float) -> CosmicBody:
        body = CosmicBody(name=name, mass=mass, position=position)
        self.bodies[name] = body
        return body

    def step(self, dt: float = 0.01):
        self.tick += 1
        self.scale_factor *= (1 + self.dark_energy_density * dt)

        for body in self.bodies.values():
            expansion_force = self.dark_energy_density * body.position * body.dark_energy_susceptibility
            gravity_force = 0.0
            for other in self.bodies.values():
                if other.name != body.name:
                    dx = other.position - body.position
                    dist = abs(dx) + 0.1
                    gravity_force += other.mass * dx / (dist * dist)

            net_force = expansion_force - gravity_force * 0.1
            body.velocity += net_force * dt
            body.position += body.velocity * dt
            body.position *= (1 + self.dark_energy_density * dt * 0.01)

        self.expansion_history.append({
            "tick": self.tick,
            "scale_factor": round(self.scale_factor, 6),
            "density": round(self.dark_energy_density, 4),
            "positions": {n: round(b.position, 3) for n, b in self.bodies.items()},
        })

    def acceleration_rate(self) -> float:
        if len(self.expansion_history) < 2:
            return 0.0
        recent = self.expansion_history[-10:]
        rates = [(recent[i]["scale_factor"] - recent[i-1]["scale_factor"])
                 for i in range(1, len(recent))]
        return sum(rates) / max(len(rates), 1)

    def state(self) -> Dict:
        return {
            "tick": self.tick,
            "scale_factor": round(self.scale_factor, 6),
            "dark_energy_density": round(self.dark_energy_density, 4),
            "acceleration": round(self.acceleration_rate(), 8),
            "bodies": len(self.bodies),
            "body_positions": {
                n: round(b.position, 3) for n, b in self.bodies.items()
            },
        }


def demo():
    engine = DarkEnergyEngine(dark_energy_density=0.7)
    print("=== Dark Energy Engine ===")

    engine.add_body("nucleus", mass=50.0, position=0.0)
    engine.add_body("agent_cluster", mass=10.0, position=5.0)
    engine.add_body("sandbox", mass=20.0, position=10.0)
    engine.add_body("protocol", mass=5.0, position=15.0)

    for _ in range(100):
        engine.step()

    state = engine.state()
    print(f"  Scale factor: {state['scale_factor']}")
    print(f"  Acceleration: {state['acceleration']}")
    print(f"  Body positions:")
    for name, pos in state["body_positions"].items():
        print(f"    {name}: {pos}")

    return state


if __name__ == "__main__":
    demo()
