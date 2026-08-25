from __future__ import annotations
"""Pollination Network — maps how ideas/code spread between modules.

Like pollen carried between flowers, code patterns and ideas spread
through function calls, imports, and copy-paste. This network maps
those transfer vectors and identifies the most prolific spreaders.
"""
import math
import json
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class PollinationEvent:
    source: str
    target: str
    idea: str
    strength: float = 1.0
    generation: int = 0

class PollinationNetwork:
    def __init__(self):
        self.modules: Dict[str, Dict] = {}
        self.events: List[PollinationEvent] = {}

    def register(self, name: str, ideas: List[str] = None):
        self.modules[name] = {"ideas": set(ideas or []), "pollination_count": 0}

    def pollinate(self, source: str, target: str, idea: str, strength: float = 1.0):
        if source in self.modules and target in self.modules:
            key = f"{source}->{target}:{idea}"
            if key not in self.events:
                self.events[key] = PollinationEvent(source, target, idea, strength)
            else:
                self.events[key].strength += strength
            self.modules[target]["ideas"].add(idea)
            self.modules[source]["pollination_count"] += 1

    def report(self) -> Dict:
        spreaders = sorted(
            [(n, m["pollination_count"]) for n, m in self.modules.items()],
            key=lambda x: x[1], reverse=True
        )
        return {
            "modules": len(self.modules),
            "total_events": len(self.events),
            "total_ideas": sum(len(m["ideas"]) for m in self.modules.values()),
            "top_spreaders": spreaders[:5],
        }


def demo():
    pn = PollinationNetwork()
    print("=== Pollination Network ===")
    pn.register("nucleus", ["state_management", "event_loop"])
    pn.register("agent", ["decision_making"])
    pn.register("sandbox", ["physics_simulation"])
    pn.pollinate("nucleus", "agent", "state_management")
    pn.pollinate("nucleus", "sandbox", "event_loop")
    pn.pollinate("agent", "sandbox", "decision_making")
    pn.pollinate("sandbox", "nucleus", "physics_simulation")
    pn.pollinate("agent", "nucleus", "state_management")
    report = pn.report()
    print(f"  Modules: {report['modules']}, Events: {report['total_events']}")
    print(f"  Top spreaders: {report['top_spreaders']}")
    return report


if __name__ == "__main__":
    demo()
