"""Reality Fabric Simulator — Simulates the fabric of the codebase's reality.

Creates a 2D fabric that can be stretched, compressed, and torn by
module interactions. The fabric's state reveals the structural integrity
of the system.
"""
from __future__ import annotations
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FabricNode:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
        self.vx = self.vy = 0.0
        self.mass = 1.0
        self.stress = 0.0


class RealityFabricSimulator:
    def __init__(self, seed=42, width=10, height=10):
        self.seed = seed
        self.rng = random.Random(seed)
        self.width, self.height = width, height
        self.nodes: list[FabricNode] = []
        self.tears: list[dict] = []
        self.tick_count = 0
        self._init_grid()

    def _init_grid(self):
        for y in range(self.height):
            for x in range(self.width):
                self.nodes.append(FabricNode(x * 0.5, y * 0.5))

    def apply_force(self, x: float, y: float, fx: float, fy: float, radius: float = 2.0):
        for node in self.nodes:
            dx = node.x - x
            dy = node.y - y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < radius and dist > 0:
                strength = 1.0 - dist / radius
                node.vx += fx * strength * 0.1
                node.vy += fy * strength * 0.1

    def tear(self, x: float, y: float):
        self.tears.append({"position": (round(x, 2), round(y, 2)), "tick": self.tick_count})

    def tick(self):
        self.tick_count += 1
        for node in self.nodes:
            node.vx *= 0.95
            node.vy *= 0.95
            node.x += node.vx
            node.y += node.vy
            node.x = max(0, min(self.width * 0.5, node.x))
            node.y = max(0, min(self.height * 0.5, node.y))
        if self.tick_count % 5 == 0:
            x = self.rng.uniform(0, self.width * 0.5)
            y = self.rng.uniform(0, self.height * 0.5)
            self.apply_force(x, y, self.rng.uniform(-0.5, 0.5), self.rng.uniform(-0.5, 0.5))

    def compute_stress(self) -> float:
        total_stress = 0.0
        for node in self.nodes:
            speed = math.sqrt(node.vx**2 + node.vy**2)
            node.stress = speed
            total_stress += speed
        return total_stress / max(1, len(self.nodes))

    def simulate(self, ticks=30):
        for _ in range(ticks):
            self.tick()
        avg_stress = self.compute_stress()
        return {
            "ticks": ticks, "nodes": len(self.nodes),
            "tears": len(self.tears), "avg_stress": round(avg_stress, 4),
        }

    def report(self) -> dict:
        return {
            "simulator": "reality_fabric_simulator",
            "grid": f"{self.width}x{self.height}",
            "nodes": len(self.nodes), "tears": len(self.tears),
            "avg_stress": round(self.compute_stress(), 4),
        }


def demo():
    sim = RealityFabricSimulator(seed=42, width=8, height=8)
    sim.apply_force(2, 2, 1.0, 0.5)
    sim.apply_force(5, 5, -0.5, 1.0)
    sim.tear(3, 4)
    r = sim.simulate(ticks=25)
    return {"simulation": r, "report": sim.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
