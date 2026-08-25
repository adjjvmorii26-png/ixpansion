from __future__ import annotations
"""Coral Reef Simulator — ecosystem growth simulation for modules.

Modules grow like coral polyps competing for resources (CPU, memory, I/O).
Symbiotic relationships emerge naturally; parasitic patterns get bleached.
The reef self-organizes into functional biomes.
"""
import math
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

@dataclass
class Polyp:
    name: str
    x: float
    y: float
    health: float = 1.0
    growth_rate: float = 0.1
    color_r: int = 0
    color_g: int = 100
    color_b: int = 200
    energy: float = 50.0
    age: int = 0
    symbionts: Set[str] = field(default_factory=set)
    parasites: Set[str] = field(default_factory=set)
    bleached: bool = False

@dataclass
class Resource:
    x: float
    y: float
    nutrient_level: float = 1.0
    light_level: float = 1.0
    current_strength: float = 0.5

@dataclass
class ReefEvent:
    event_type: str
    polyp_name: str
    detail: str
    tick: int

class CoralReefSimulator:
    def __init__(self, width: float = 100.0, height: float = 100.0,
                 seed: int = 42):
        self.width = width
        self.height = height
        self.rng = random.Random(seed)
        self.polyps: Dict[str, Polyp] = {}
        self.resources: List[Resource] = []
        self.events: List[ReefEvent] = []
        self.tick_count = 0
        self._init_resources()

    def _init_resources(self, num_resources: int = 20):
        for _ in range(num_resources):
            self.resources.append(Resource(
                x=self.rng.uniform(0, self.width),
                y=self.rng.uniform(0, self.height),
                nutrient_level=self.rng.uniform(0.3, 1.0),
                light_level=self.rng.uniform(0.2, 1.0),
            ))

    def _distance(self, a_x: float, a_y: float, b_x: float, b_y: float) -> float:
        return math.sqrt((a_x - b_x) ** 2 + (a_y - b_y) ** 2)

    def spawn_polyp(self, name: str, x: float = None, y: float = None,
                    growth_rate: float = 0.1) -> Polyp:
        px = x if x is not None else self.rng.uniform(10, self.width - 10)
        py = y if y is not None else self.rng.uniform(10, self.height - 10)
        hash_val = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
        polyp = Polyp(
            name=name, x=px, y=py, growth_rate=growth_rate,
            color_r=hash_val % 256,
            color_g=(hash_val >> 8) % 256,
            color_b=(hash_val >> 16) % 256,
            energy=50.0,
        )
        self.polyps[name] = polyp
        self.events.append(ReefEvent("spawn", name, f"Born at ({px:.1f}, {py:.1f})", self.tick_count))
        return polyp

    def _gather_resources(self, polyp: Polyp) -> float:
        energy_gain = 0.0
        for res in self.resources:
            dist = self._distance(polyp.x, polyp.y, res.x, res.y)
            if dist < 20.0:
                influence = 1.0 - dist / 20.0
                energy_gain += (res.nutrient_level * res.light_level * influence * 2.0)
        return energy_gain

    def _check_symbiosis(self, a: Polyp, b: Polyp) -> bool:
        dist = self._distance(a.x, a.y, b.x, b.y)
        if dist > 15.0:
            return False
        color_sim = 1.0 - (
            abs(a.color_r - b.color_r) +
            abs(a.color_g - b.color_g) +
            abs(a.color_b - b.color_b)
        ) / 765.0
        return color_sim > 0.7 and self.rng.random() < 0.3

    def advance_tick(self) -> List[ReefEvent]:
        self.tick_count += 1
        tick_events = []

        for name, polyp in self.polyps.items():
            if polyp.bleached:
                polyp.health -= 0.02
                if polyp.health <= 0:
                    tick_events.append(ReefEvent("death", name, "Fully bleached", self.tick_count))
                    continue

            energy_gain = self._gather_resources(polyp)
            polyp.energy += energy_gain

            growth_cost = polyp.growth_rate * polyp.energy * 0.01
            polyp.energy -= growth_cost
            polyp.health = min(1.0, polyp.health + polyp.growth_rate * 0.01)

            polyp.age += 1

            if polyp.energy > 80 and self.rng.random() < 0.1:
                child_name = f"{name}_gen{self.tick_count}"
                offset_x = self.rng.uniform(-5, 5)
                offset_y = self.rng.uniform(-5, 5)
                child_x = max(0, min(self.width, polyp.x + offset_x))
                child_y = max(0, min(self.height, polyp.y + offset_y))
                self.spawn_polyp(child_name, child_x, child_y, polyp.growth_rate * 0.95)
                polyp.energy -= 30
                tick_events.append(ReefEvent("reproduction", name,
                    f"Spawned {child_name}", self.tick_count))

            if polyp.energy < 10:
                polyp.health -= 0.05
                if polyp.health <= 0 and not polyp.bleached:
                    polyp.bleached = True
                    tick_events.append(ReefEvent("bleach", name, "Energy depleted", self.tick_count))

            if polyp.energy > 100:
                polyp.bleached = False
                polyp.health = min(1.0, polyp.health + 0.1)

        names = list(self.polyps.keys())
        for i, na in enumerate(names):
            for nb in names[i + 1:]:
                a, b = self.polyps[na], self.polyps[nb]
                if self._check_symbiosis(a, b):
                    if nb not in a.symbionts:
                        a.symbionts.add(nb)
                        b.symbionts.add(na)
                        a.health = min(1.0, a.health + 0.05)
                        b.health = min(1.0, b.health + 0.05)
                        tick_events.append(ReefEvent("symbiosis", na,
                            f"Partnered with {nb}", self.tick_count))

        self.events.extend(tick_events)
        return tick_events

    def run_simulation(self, ticks: int) -> Dict[str, any]:
        for _ in range(ticks):
            self.advance_tick()

        alive = [p for p in self.polyps.values() if not p.bleached and p.health > 0]
        bleached = [p for p in self.polyps.values() if p.bleached]
        dead = ticks - len(alive) - len(bleached)

        return {
            "ticks": ticks,
            "alive": len(alive),
            "bleached": len(bleached),
            "dead": dead,
            "total_events": len(self.events),
            "symbioses": sum(1 for p in alive if p.symbionts),
            "avg_health": sum(p.health for p in alive) / max(len(alive), 1),
        }

    def reef_map(self) -> List[Dict]:
        return [
            {"name": p.name, "x": round(p.x, 1), "y": round(p.y, 1),
             "health": round(p.health, 3), "energy": round(p.energy, 1),
             "bleached": p.bleached, "age": p.age,
             "symbionts": len(p.symbionts)}
            for p in sorted(self.polyps.values(), key=lambda p: p.health, reverse=True)
            if p.health > 0
        ]


def demo():
    reef = CoralReefSimulator(width=50, height=50, seed=42)
    print("=== Coral Reef Simulator ===")
    seed_polyps = ["brain_coral", "staghorn", "fire_coral", "sea_fan", "mushroom"]
    for name in seed_polyps:
        reef.spawn_polyp(name)

    print(f"Spawned {len(reef.polyps)} seed polyps")
    results = reef.run_simulation(ticks=10)
    print(f"\nAfter {results['ticks']} ticks:")
    print(f"  Alive: {results['alive']}, Bleached: {results['bleached']}")
    print(f"  Symbioses: {results['symbioses']}, Avg health: {results['avg_health']:.3f}")
    print(f"  Total events: {results['total_events']}")

    print("\nTop 5 healthiest polyps:")
    for p in reef.reef_map()[:5]:
        print(f"  {p['name']}: health={p['health']}, energy={p['energy']}, "
              f"symbionts={p['symbionts']}")

    return results


if __name__ == "__main__":
    demo()
