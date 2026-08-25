"""Consciousness Field — Models awareness as a continuous field across the system.

Unlike the discrete neuron simulator, this models consciousness as a
continuous field that flows through the codebase, with varying intensity
based on module density and connection strength.
"""
from __future__ import annotations
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ConsciousnessField:
    def __init__(self, seed=42, grid_size=20):
        self.seed = seed
        self.rng = random.Random(seed)
        self.grid_size = grid_size
        self.field = [[0.0] * grid_size for _ in range(grid_size)]
        self.wells: list[dict] = []
        self.tick_count = 0

    def add_well(self, x: float, y: float, strength: float, name: str = ""):
        self.wells.append({"x": x, "y": y, "strength": strength, "name": name})

    def compute_field(self):
        for gy in range(self.grid_size):
            for gx in range(self.grid_size):
                fx = gx * 0.5
                fy = gy * 0.5
                total = 0.0
                for well in self.wells:
                    dx = fx - well["x"]
                    dy = fy - well["y"]
                    dist = math.sqrt(dx*dx + dy*dy) + 0.1
                    total += well["strength"] / (dist * dist)
                self.field[gy][gx] = min(1.0, total)

    def tick(self):
        self.tick_count += 1
        for well in self.wells:
            well["strength"] += self.rng.uniform(-0.05, 0.05)
            well["strength"] = max(0.1, min(2.0, well["strength"]))
        self.compute_field()

    def get_hotspots(self, threshold: float = 0.5) -> list[dict]:
        hotspots = []
        for gy in range(self.grid_size):
            for gx in range(self.grid_size):
                if self.field[gy][gx] > threshold:
                    hotspots.append({
                        "position": (gx, gy),
                        "intensity": round(self.field[gy][gx], 4),
                    })
        hotspots.sort(key=lambda h: h["intensity"], reverse=True)
        return hotspots[:10]

    def awareness_level(self) -> float:
        total = sum(sum(row) for row in self.field)
        max_possible = self.grid_size * self.grid_size
        return round(total / max_possible, 4)

    def simulate(self, ticks=20):
        for _ in range(ticks):
            self.tick()
        return {
            "ticks": ticks,
            "awareness": self.awareness_level(),
            "hotspots": len(self.get_hotspots()),
            "wells": len(self.wells),
        }

    def report(self) -> dict:
        hotspots = self.get_hotspots()
        return {
            "field": "consciousness_field",
            "grid_size": self.grid_size,
            "wells": len(self.wells),
            "awareness": self.awareness_level(),
            "hotspots": hotspots[:5],
        }


def demo():
    field = ConsciousnessField(seed=42, grid_size=15)
    rng = random.Random(42)
    for i in range(8):
        field.add_well(rng.uniform(0, 7), rng.uniform(0, 7), rng.uniform(0.5, 1.5), f"module_{i}")
    sim = field.simulate(ticks=15)
    return {"simulation": sim, "report": field.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
