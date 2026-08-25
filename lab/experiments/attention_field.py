"""Attention Field — Models which parts of the codebase attract the most focus.

Like a gravitational field, modules with more connections, more tests,
and more recent changes exert stronger "pull" on developer attention.
"""
from __future__ import annotations
import hashlib
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class AttentionField:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.wells: list[dict] = []

    def add_gravitational_well(self, name: str, mass: float, position: tuple[int, int] = (0, 0)):
        self.wells.append({"name": name, "mass": mass, "position": position})

    def field_strength_at(self, point: tuple[int, int]) -> float:
        strength = 0.0
        for well in self.wells:
            dx = point[0] - well["position"][0]
            dy = point[1] - well["position"][1]
            dist = math.sqrt(dx * dx + dy * dy) + 0.1
            strength += well["mass"] / (dist * dist)
        return strength

    def find_hotspots(self, grid_size: int = 10) -> list[dict]:
        hotspots = []
        for y in range(grid_size):
            for x in range(grid_size):
                strength = self.field_strength_at((x, y))
                if strength > 0.5:
                    hotspots.append({"x": x, "y": y, "strength": round(strength, 4)})
        hotspots.sort(key=lambda h: h["strength"], reverse=True)
        return hotspots[:10]

    def report(self) -> dict:
        hotspots = self.find_hotspots()
        total_mass = sum(w["mass"] for w in self.wells)
        return {
            "attention_field": "attention_field",
            "well_count": len(self.wells),
            "total_mass": round(total_mass, 4),
            "hotspots": hotspots,
            "hottest": hotspots[0] if hotspots else None,
        }


def demo():
    field = AttentionField(seed=42)
    # Map modules as gravitational wells
    dirs = {"api": ROOT / "api", "lab": ROOT / "lab" / "experiments", "bridges": ROOT / "bridges"}
    pos = 0
    for subsys, base in dirs.items():
        if base.exists():
            for py in base.glob("*.py"):
                if py.name.startswith("_"):
                    continue
                size = py.stat().st_size
                mass = size / 5000.0
                field.add_gravitational_well(py.stem, mass, (pos % 10, pos // 10))
                pos += 1
    return field.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
