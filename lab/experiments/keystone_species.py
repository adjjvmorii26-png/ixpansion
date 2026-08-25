from __future__ import annotations
"""Keystone Species — identifies modules whose removal collapses the system.

Like keystone species in ecology whose removal causes ecosystem collapse,
some code modules are critical dependencies. This module identifies them
by measuring the cascade effect of removing each module.
"""
import math
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set

@dataclass
class ModuleNode:
    name: str
    dependents: Set[str] = field(default_factory=set)
    dependencies: Set[str] = field(default_factory=set)
    health: float = 1.0
    criticality: float = 0.0

class KeystoneDetector:
    def __init__(self):
        self.modules: Dict[str, ModuleNode] = {}

    def add_module(self, name: str, dependents: List[str] = None,
                   dependencies: List[str] = None):
        node = ModuleNode(name=name,
                         dependents=set(dependents or []),
                         dependencies=set(dependencies or []))
        self.modules[name] = node

    def _cascade_count(self, removed: str) -> int:
        affected = set()
        queue = [removed]
        while queue:
            current = queue.pop()
            for name, node in self.modules.items():
                if current in node.dependencies and name not in affected:
                    affected.add(name)
                    queue.append(name)
        return len(affected)

    def assess(self) -> Dict[str, float]:
        scores = {}
        for name in self.modules:
            direct = len(self.modules[name].dependents)
            cascade = self._cascade_count(name)
            total = self.modules[name].dependencies | self.modules[name].dependents
            connectivity = len(total) / max(len(self.modules) - 1, 1)
            scores[name] = round(connectivity * 0.4 + direct * 0.1 + cascade * 0.5, 4)
            self.modules[name].criticality = scores[name]
        return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

    def top_keystone(self, n: int = 5) -> List[Dict]:
        scores = self.assess()
        return [{"name": k, "criticality": v} for k, v in list(scores.items())[:n]]


def demo():
    detector = KeystoneDetector()
    print("=== Keystone Species Detector ===")
    modules = {
        "nucleus": {"deps": [], "dependents": ["agent", "sandbox", "protocol"]},
        "agent": {"deps": ["nucleus"], "dependents": ["observer"]},
        "sandbox": {"deps": ["nucleus"], "dependents": ["simulator"]},
        "protocol": {"deps": ["nucleus"], "dependents": ["messenger"]},
        "observer": {"deps": ["agent", "sandbox"], "dependents": ["logger"]},
        "logger": {"deps": ["observer"], "dependents": []},
        "simulator": {"deps": ["sandbox"], "dependents": ["observer"]},
        "messenger": {"deps": ["protocol"], "dependents": []},
    }
    for name, info in modules.items():
        detector.add_module(name, info["dependents"], info["deps"])
    top = detector.top_keystone(5)
    print("  Top keystone species:")
    for t in top:
        print(f"    {t['name']}: criticality={t['criticality']}")
    return {"keystones": top}


if __name__ == "__main__":
    demo()
