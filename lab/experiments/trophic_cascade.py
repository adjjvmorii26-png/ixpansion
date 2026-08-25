from __future__ import annotations
"""Trophic Cascade — models chain reactions when one module changes.

Like trophic cascades in ecology where removing a predator causes
herbivore explosions that devastate plants, changing one module can
trigger cascading effects through the dependency chain.
"""
import math
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set

@dataclass
class TrophicLevel:
    level: int
    modules: List[str]

class TrophicCascadeSimulator:
    def __init__(self):
        self.modules: Dict[str, Dict] = {}
        self.levels: List[TrophicLevel] = []

    def add_module(self, name: str, level: int, consumes: List[str] = None,
                   health: float = 1.0):
        self.modules[name] = {
            "level": level, "consumes": set(consumes or []),
            "health": health, "affected": False,
        }

    def trigger_cascade(self, changed_module: str, change_magnitude: float = -0.5) -> List[Dict]:
        effects = []
        queue = [(changed_module, change_magnitude)]
        visited = set()
        while queue:
            mod, magnitude = queue.pop(0)
            if mod in visited or mod not in self.modules:
                continue
            visited.add(mod)
            old_health = self.modules[mod]["health"]
            self.modules[mod]["health"] = max(0, min(1, old_health + magnitude))
            self.modules[mod]["affected"] = True
            effects.append({
                "module": mod, "old_health": round(old_health, 3),
                "new_health": round(self.modules[mod]["health"], 3),
                "magnitude": magnitude,
            })
            for name, info in self.modules.items():
                if mod in info["consumes"] and name not in visited:
                    cascade_mag = magnitude * 0.5
                    queue.append((name, cascade_mag))
        return effects

    def report(self) -> Dict:
        affected = sum(1 for m in self.modules.values() if m["affected"])
        avg_health = sum(m["health"] for m in self.modules.values()) / max(len(self.modules), 1)
        return {
            "modules": len(self.modules),
            "affected": affected,
            "avg_health": round(avg_health, 3),
        }


def demo():
    sim = TrophicCascadeSimulator()
    print("=== Trophic Cascade Simulator ===")
    sim.add_module("nucleus", 0, [], 1.0)
    sim.add_module("agent", 1, ["nucleus"], 1.0)
    sim.add_module("sandbox", 1, ["nucleus"], 1.0)
    sim.add_module("observer", 2, ["agent", "sandbox"], 1.0)
    sim.add_module("logger", 3, ["observer"], 1.0)
    effects = sim.trigger_cascade("nucleus", -0.6)
    print(f"  Cascade effects from nucleus change:")
    for e in effects:
        print(f"    {e['module']}: {e['old_health']} → {e['new_health']} "
              f"(magnitude={e['magnitude']})")
    report = sim.report()
    print(f"  Affected: {report['affected']}/{report['modules']}, "
          f"avg health: {report['avg_health']}")
    return report


if __name__ == "__main__":
    demo()
