"""Gravitational Lens — Bends code paths around massive modules.

Models how large, complex modules bend the "light" (execution paths)
of smaller modules around them, creating lensing effects that reveal
hidden structure.
"""
from __future__ import annotations
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GravitationalLens:
    def __init__(self, seed=42):
        self.seed = seed
        self.lenses: list[dict] = []
        self.rays: list[dict] = []

    def add_lens(self, name: str, x: float, y: float, mass: float):
        self.lenses.append({"name": name, "x": x, "y": y, "mass": mass})

    def trace_ray(self, start_x: float, start_y: float, direction_x: float, direction_y: float, steps: int = 20) -> dict:
        path = [(start_x, start_y)]
        x, y = start_x, start_y
        dx, dy = direction_x, direction_y
        total_deflection = 0.0
        for _ in range(steps):
            for lens in self.lenses:
                lx, ly = lens["x"], lens["y"]
                dist = math.sqrt((x-lx)**2 + (y-ly)**2) + 0.1
                force = lens["mass"] / (dist * dist)
                dx += force * (lx - x) / dist * 0.1
                dy += force * (ly - y) / dist * 0.1
                total_deflection += force * 0.1
            speed = math.sqrt(dx*dx + dy*dy)
            if speed > 0:
                dx, dy = dx/speed * 0.5, dy/speed * 0.5
            x += dx
            y += dy
            path.append((round(x, 3), round(y, 3)))
        self.rays.append({
            "start": (start_x, start_y), "end": (x, y),
            "deflection": round(total_deflection, 4), "path_length": len(path),
        })
        return {"path": path, "deflection": round(total_deflection, 4)}

    def report(self) -> dict:
        avg_deflection = sum(r["deflection"] for r in self.rays) / max(1, len(self.rays))
        return {
            "lens": "gravitational_lens",
            "lenses": len(self.lenses),
            "rays_traced": len(self.rays),
            "avg_deflection": round(avg_deflection, 4),
            "strongest_lens": max(self.lenses, key=lambda l: l["mass"]) if self.lenses else None,
            "rays": self.rays[:5],
        }


def demo():
    lens = GravitationalLens(seed=42)
    import random
    rng = random.Random(42)
    for i in range(5):
        lens.add_lens(f"module_{i}", rng.uniform(-5, 5), rng.uniform(-5, 5), rng.uniform(1, 5))
    for i in range(8):
        lens.trace_ray(rng.uniform(-10, 10), -10, rng.uniform(-0.1, 0.1), 1.0)
    return lens.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
