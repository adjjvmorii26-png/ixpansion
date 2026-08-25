"""Cosmic Fabric Weaver — Weaves the fabric of the codebase's spacetime.

Creates a 2D spacetime manifold where modules are points, and the
fabric between them is warped by their mass and connections.
"""
from __future__ import annotations
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SpacetimePoint:
    def __init__(self, name: str, x: float, y: float, mass: float):
        self.name = name
        self.x, self.y = x, y
        self.mass = mass
        self.curvature = 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name, "position": (round(self.x, 2), round(self.y, 2)),
            "mass": round(self.mass, 3), "curvature": round(self.curvature, 4),
        }


class CosmicFabricWeaver:
    def __init__(self, seed=42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.points: list[SpacetimePoint] = []
        self.connections: list[tuple[str, str]] = []
        self.geodesics: list[dict] = []

    def weave_point(self, name: str, filepath: Path):
        text = filepath.read_text(errors="replace")
        mass = len(text.splitlines()) / 100.0
        x = self.rng.uniform(-10, 10)
        y = self.rng.uniform(-10, 10)
        self.points.append(SpacetimePoint(name, x, y, mass))

    def compute_curvature(self):
        for p in self.points:
            curvature = 0.0
            for other in self.points:
                if other is not p:
                    dx = other.x - p.x
                    dy = other.y - p.y
                    dist = math.sqrt(dx*dx + dy*dy) + 0.1
                    curvature += other.mass / (dist * dist)
            p.curvature = curvature

    def compute_geodesics(self):
        self.geodesics = []
        for i in range(len(self.points) - 1):
            a, b = self.points[i], self.points[i+1]
            dist = math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2)
            curvature_mid = (a.curvature + b.curvature) / 2
            deflection = curvature_mid * dist * 0.1
            self.geodesics.append({
                "from": a.name, "to": b.name,
                "distance": round(dist, 3),
                "deflection": round(deflection, 4),
            })

    def report(self) -> dict:
        self.compute_curvature()
        self.compute_geodesics()
        avg_curvature = sum(p.curvature for p in self.points) / max(1, len(self.points))
        return {
            "fabric": "cosmic_fabric_weaver",
            "points": len(self.points), "point_count": len(self.points),
            "geodesics": len(self.geodesics),
            "avg_curvature": round(avg_curvature, 4),
            "most_curved": max(self.points, key=lambda p: p.curvature).to_dict() if self.points else None,
            "flattest": min(self.points, key=lambda p: p.curvature).to_dict() if self.points else None,
            "points": [p.to_dict() for p in sorted(self.points, key=lambda p: p.curvature, reverse=True)[:8]],
        }


def demo():
    weaver = CosmicFabricWeaver(seed=42)
    for py in list((ROOT / "lab").glob("*.py"))[:8]:
        if not py.name.startswith("_"):
            weaver.weave_point(py.stem, py)
    for py in list((ROOT / "api").glob("*.py"))[:5]:
        if not py.name.startswith("_"):
            weaver.weave_point(py.stem, py)
    return weaver.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
