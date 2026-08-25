from __future__ import annotations
"""Time Dilation Field — relativistic time effects across modules.

Some modules experience time faster or slower than others based on their
"mass" (complexity) and "velocity" (change rate). Heavy, fast-changing
modules experience time dilation, processing fewer ticks per unit of
observer time. Creates temporal hierarchies in the system.
"""
import math
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

C = 299792458.0  # Speed of light (scaled)
TIME_SCALE = 1000.0

@dataclass
class TemporalBody:
    name: str
    mass: float = 1.0
    velocity: float = 0.0
    proper_time: float = 0.0
    coordinate_time: float = 0.0
    time_dilation_factor: float = 1.0
    ticks_completed: int = 0
    events: List[str] = field(default_factory=list)

    @property
    def lorentz_factor(self) -> float:
        v_ratio = min(self.velocity / C, 0.9999)
        return 1.0 / math.sqrt(1.0 - v_ratio ** 2)

    @property
    def gravitational_dilation(self) -> float:
        schwarzschild = 2.0 * self.mass / (C ** 2 / TIME_SCALE)
        if schwarzschild >= 1.0:
            return 0.001
        return math.sqrt(1.0 - schwarzschild)

    @property
    def total_dilation(self) -> float:
        return self.lorentz_factor * self.gravitational_dilation


class TimeDilationField:
    def __init__(self, observer_rate: float = 1.0):
        self.observer_rate = observer_rate
        self.bodies: Dict[str, TemporalBody] = {}
        self.observer_time = 0.0
        self.tick = 0
        self.timeline: List[Dict] = []

    def add_body(self, name: str, mass: float = 1.0, velocity: float = 0.0) -> TemporalBody:
        body = TemporalBody(name=name, mass=mass, velocity=velocity)
        self.bodies[name] = body
        return body

    def set_velocity(self, name: str, velocity: float):
        if name in self.bodies:
            self.bodies[name].velocity = min(velocity, C * 0.9999)

    def step(self, dt: float = 1.0):
        self.tick += 1
        self.observer_time += dt

        for name, body in self.bodies.items():
            dilation = body.total_dilation
            proper_dt = dt * dilation * self.observer_rate
            body.proper_time += proper_dt
            body.time_dilation_factor = dilation

            if body.proper_time >= 1.0:
                ticks_to_process = int(body.proper_time)
                body.ticks_completed += ticks_to_process
                body.proper_time -= ticks_to_process
                body.events.append(f"tick_{self.tick}")

            body.coordinate_time = self.observer_time

        self.timeline.append({
            "tick": self.tick,
            "observer_time": round(self.observer_time, 4),
            "bodies": {
                name: {
                    "proper_time": round(b.proper_time, 4),
                    "dilation": round(b.total_dilation, 6),
                    "ticks": b.ticks_completed,
                }
                for name, b in self.bodies.items()
            },
        })

    def temporal_map(self) -> List[Dict]:
        return sorted([
            {"name": b.name, "mass": b.mass, "velocity": b.velocity,
             "dilation": round(b.total_dilation, 6),
             "ticks_completed": b.ticks_completed,
             "proper_time": round(b.proper_time, 4)}
            for b in self.bodies.values()
        ], key=lambda x: x["dilation"])

    def run(self, steps: int, dt: float = 1.0) -> Dict:
        for _ in range(steps):
            self.step(dt)
        fastest = max(self.bodies.values(), key=lambda b: b.ticks_completed)
        slowest = min(self.bodies.values(), key=lambda b: b.ticks_completed)
        return {
            "steps": steps,
            "observer_time": round(self.observer_time, 4),
            "fastest": fastest.name,
            "slowest": slowest.name,
            "fastest_ticks": fastest.ticks_completed,
            "slowest_ticks": slowest.ticks_completed,
            "temporal_spread": fastest.ticks_completed - slowest.ticks_completed,
            "map": self.temporal_map(),
        }


def demo():
    field_engine = TimeDilationField(observer_rate=1.0)
    print("=== Time Dilation Field ===")

    field_engine.add_body("photon_core", mass=50.0, velocity=0)
    field_engine.add_body("agent_alpha", mass=1.0, velocity=100000)
    field_engine.add_body("agent_beta", mass=2.0, velocity=200000)
    field_engine.add_body("light_runner", mass=0.1, velocity=C * 0.9)
    field_engine.add_body("heavy_static", mass=100.0, velocity=0)

    result = field_engine.run(steps=50, dt=1.0)
    print(f"  Steps: {result['steps']}, Observer time: {result['observer_time']}")
    print(f"  Fastest: {result['fastest']} ({result['fastest_ticks']} ticks)")
    print(f"  Slowest: {result['slowest']} ({result['slowest_ticks']} ticks)")
    print(f"  Temporal spread: {result['temporal_spread']} ticks")

    print("\nTemporal map:")
    for entry in result["map"]:
        print(f"  {entry['name']}: dilation={entry['dilation']}, "
              f"ticks={entry['ticks_completed']}, mass={entry['mass']}")

    return result


if __name__ == "__main__":
    demo()
