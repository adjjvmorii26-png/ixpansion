"""Spacetime Manifold — 4D spacetime model of the codebase.

Creates a 4D manifold (3 space + 1 time) where modules exist as
events in spacetime, connected by light cones and world lines.
"""
from __future__ import annotations
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SpacetimeEvent:
    def __init__(self, name: str, x: float, y: float, z: float, t: float):
        self.name = name
        self.x, self.y, self.z, self.t = x, y, z, t
        self.world_line: list[tuple[float, float, float, float]] = [(x, y, z, t)]

    def move(self, dx: float, dy: float, dz: float, dt: float):
        self.x += dx; self.y += dy; self.z += dz; self.t += dt
        self.world_line.append((self.x, self.y, self.z, self.t))

    def invariant_interval(self, other: "SpacetimeEvent") -> float:
        ds2 = -(self.t - other.t)**2 + (self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2
        return ds2

    def to_dict(self) -> dict:
        return {"name": self.name, "position": (round(self.x, 2), round(self.y, 2), round(self.z, 2)),
                "time": round(self.t, 2), "world_line_length": len(self.world_line)}


class SpacetimeManifold:
    def __init__(self, seed=42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.events: list[SpacetimeEvent] = []
        self.light_cones: list[dict] = []

    def add_event(self, name: str, x: float = 0, y: float = 0, z: float = 0, t: float = 0):
        self.events.append(SpacetimeEvent(name, x, y, z, t))

    def compute_light_cones(self):
        self.light_cones = []
        for i, a in enumerate(self.events):
            for b in self.events[i+1:]:
                ds2 = a.invariant_interval(b)
                if abs(ds2) < 0.01:
                    relation = "lightlike"
                elif ds2 > 0:
                    relation = "spacelike"
                else:
                    relation = "timelike"
                self.light_cones.append({"a": a.name, "b": b.name, "interval": round(ds2, 4), "relation": relation})

    def simulate(self, ticks=15):
        for _ in range(ticks):
            for event in self.events:
                event.move(self.rng.uniform(-0.2, 0.2), self.rng.uniform(-0.2, 0.2),
                          self.rng.uniform(-0.2, 0.2), 1.0)
        self.compute_light_cones()
        relations = {}
        for lc in self.light_cones:
            r = lc["relation"]
            relations[r] = relations.get(r, 0) + 1
        return {
            "ticks": ticks, "events": len(self.events),
            "light_cones": len(self.light_cones), "relations": relations,
        }

    def report(self) -> dict:
        return {
            "manifold": "spacetime_manifold",
            "events": len(self.events), "light_cones": len(self.light_cones),
            "events_detail": [e.to_dict() for e in self.events[:5]],
        }


def demo():
    manifold = SpacetimeManifold(seed=42)
    for i in range(8):
        manifold.add_event(f"event_{i}", manifold.rng.uniform(-5, 5),
                          manifold.rng.uniform(-5, 5), manifold.rng.uniform(-5, 5), 0)
    sim = manifold.simulate(ticks=15)
    return {"simulation": sim, "report": manifold.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
