from __future__ import annotations
"""Neural Dust — microscopic agents that scatter through the system.

Thousands of tiny "dust particles" spread through the system, each
collecting local state information. When particles collide, they
exchange data, creating emergent global awareness from local sensing.
Like neural dust in bioelectric networks.
"""
import math
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class DustParticle:
    particle_id: str
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    memory: List[str] = field(default_factory=list)
    energy: float = 10.0
    age: int = 0
    collisions: int = 0

    def sense(self, environment: Dict) -> str:
        report = f"{self.particle_id}:{environment.get('zone', 'unknown')}"
        self.memory.append(report)
        if len(self.memory) > 20:
            self.memory.pop(0)
        return report

    def move(self, width: float, height: float, friction: float = 0.98):
        self.x += self.vx
        self.y += self.vy
        self.vx *= friction
        self.vy *= friction
        self.x = self.x % width
        self.y = self.y % height
        self.age += 1
        self.energy -= 0.1

class NeuralDustCloud:
    def __init__(self, width: float = 100, height: float = 100,
                 num_particles: int = 50, seed: int = 42):
        self.width = width
        self.height = height
        self.rng = random.Random(seed)
        self.particles: List[DustParticle] = []
        self.collisions_log: List[Dict] = []
        self.tick = 0
        self.global_memory: Dict[str, int] = {}

        for i in range(num_particles):
            p = DustParticle(
                particle_id=f"dust_{i:04d}",
                x=self.rng.uniform(0, width),
                y=self.rng.uniform(0, height),
                vx=self.rng.uniform(-0.5, 0.5),
                vy=self.rng.uniform(-0.5, 0.5),
            )
            self.particles.append(p)

    def _collision_distance(self, a: DustParticle, b: DustParticle) -> float:
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

    def _exchange_data(self, a: DustParticle, b: DustParticle):
        shared = set(a.memory[-5:]) & set(b.memory[-5:])
        a.memory.extend(list(set(b.memory[-5:]) - set(a.memory)))
        b.memory.extend(list(set(a.memory[-5:]) - set(b.memory)))
        a.memory = a.memory[-20:]
        b.memory = b.memory[-20:]
        a.collisions += 1
        b.collisions += 1
        a.energy += 1.0
        b.energy += 1.0

    def sense_environment(self, zones: Dict[str, Tuple[float, float, float, float]]):
        for p in self.particles:
            for zone_name, (x1, y1, x2, y2) in zones.items():
                if x1 <= p.x <= x2 and y1 <= p.y <= y2:
                    p.sense({"zone": zone_name})
                    break

    def step(self, collision_radius: float = 3.0):
        self.tick += 1
        for p in self.particles:
            p.move(self.width, self.height)
            p.vx += self.rng.gauss(0, 0.1)
            p.vy += self.rng.gauss(0, 0.1)

        for i, a in enumerate(self.particles):
            for b in self.particles[i + 1:]:
                if self._collision_distance(a, b) < collision_radius:
                    self._exchange_data(a, b)
                    self.collisions_log.append({
                        "tick": self.tick,
                        "a": a.particle_id, "b": b.particle_id,
                    })

        for p in self.particles:
            for mem in p.memory:
                key = mem.split(":")[1] if ":" in mem else mem
                self.global_memory[key] = self.global_memory.get(key, 0) + 1

        self.particles = [p for p in self.particles if p.energy > 0]

    def awareness_map(self) -> Dict[str, int]:
        return dict(sorted(self.global_memory.items(), key=lambda x: x[1], reverse=True))

    def cloud_stats(self) -> Dict:
        alive = [p for p in self.particles if p.energy > 0]
        return {
            "tick": self.tick,
            "particles_alive": len(alive),
            "total_collisions": len(self.collisions_log),
            "avg_memory": sum(len(p.memory) for p in alive) / max(len(alive), 1),
            "avg_energy": sum(p.energy for p in alive) / max(len(alive), 1),
            "awareness_zones": len(self.global_memory),
        }

    def run(self, steps: int, zones: Dict = None) -> Dict:
        for _ in range(steps):
            if zones:
                self.sense_environment(zones)
            self.step()
        return self.cloud_stats()


def demo():
    cloud = NeuralDustCloud(width=50, height=50, num_particles=30, seed=42)
    print("=== Neural Dust Cloud ===")

    zones = {
        "nucleus": (20, 20, 30, 30),
        "agent_zone": (5, 5, 15, 15),
        "sandbox": (35, 35, 45, 45),
    }

    stats = cloud.run(steps=20, zones=zones)
    print(f"  Particles alive: {stats['particles_alive']}")
    print(f"  Collisions: {stats['total_collisions']}")
    print(f"  Avg memory: {stats['avg_memory']:.1f}")
    print(f"  Awareness zones: {stats['awareness_zones']}")

    awareness = cloud.awareness_map()
    print("\nAwareness map:")
    for zone, count in list(awareness.items())[:5]:
        print(f"  {zone}: {count}")

    return stats


if __name__ == "__main__":
    demo()
