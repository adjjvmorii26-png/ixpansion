"""Gravitational Time Dilation — Code runs faster/slower based on local complexity.

Models how code execution speed varies based on the "gravitational mass"
of surrounding complexity. Simple functions run fast; complex ones slow down.
"""
from __future__ import annotations
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CodeBody:
    def __init__(self, name: str, mass: float, complexity: float):
        self.name = name
        self.mass = mass
        self.complexity = complexity
        self.time_dilation = 1.0
        self.execution_time = 0.0

    def compute_dilation(self, nearby_mass: float, c: float = 1.0):
        rs = 2 * self.mass / (c * c) if c > 0 else 0
        self.time_dilation = 1.0 / math.sqrt(max(0.01, 1 - rs / max(0.01, nearby_mass + 1)))
        self.execution_time = self.time_dilation * self.complexity

    def to_dict(self) -> dict:
        return {
            "name": self.name, "mass": round(self.mass, 3),
            "complexity": round(self.complexity, 3),
            "dilation": round(self.time_dilation, 4),
            "exec_time": round(self.execution_time, 4),
        }


class GravitationalTimeDilation:
    def __init__(self, seed=42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.bodies: list[CodeBody] = []

    def add_body(self, name: str, filepath: Path):
        text = filepath.read_text(errors="replace")
        lines = len(text.splitlines())
        funcs = sum(1 for l in text.splitlines() if l.strip().startswith("def "))
        mass = lines / 100.0
        complexity = funcs / max(1, lines / 50)
        self.bodies.append(CodeBody(name, mass, complexity))

    def compute_dilations(self):
        total_mass = sum(b.mass for b in self.bodies)
        for body in self.bodies:
            nearby = total_mass - body.mass
            body.compute_dilation(nearby)

    def report(self) -> dict:
        self.compute_dilations()
        self.bodies.sort(key=lambda b: b.time_dilation, reverse=True)
        return {
            "dilation": "gravitational_time_dilation",
            "bodies": len(self.bodies), "body_count": len(self.bodies),
            "fastest": self.bodies[-1].to_dict() if self.bodies else None,
            "slowest": self.bodies[0].to_dict() if self.bodies else None,
            "avg_dilation": round(
                sum(b.time_dilation for b in self.bodies) / max(1, len(self.bodies)), 4
            ),
            "bodies": [b.to_dict() for b in self.bodies[:10]],
        }


def demo():
    gtd = GravitationalTimeDilation(seed=42)
    for py in list((ROOT / "lab").glob("*.py"))[:10]:
        if not py.name.startswith("_"):
            gtd.add_body(py.stem, py)
    for py in list((ROOT / "api").glob("*.py"))[:5]:
        if not py.name.startswith("_"):
            gtd.add_body(py.stem, py)
    return gtd.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
