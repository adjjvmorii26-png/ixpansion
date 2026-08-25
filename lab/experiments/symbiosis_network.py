from __future__ import annotations
"""Symbiosis Network — maps mutualistic, commensal, and parasitic relationships.

Like biological symbiosis (mutualism, commensalism, parasitism), modules
have relationships where both benefit, one benefits harmlessly, or one
benefits at the other's expense.
"""
import math
import json
from dataclasses import dataclass, field
from typing import Dict, List

class RelType:
    MUTUAL = "mutualism"
    COMMENSAL = "commensalism"
    PARASITIC = "parasitism"
    COMPETITIVE = "competition"

@dataclass
class SymbiosisRelation:
    module_a: str
    module_b: str
    rel_type: str
    benefit_a: float
    benefit_b: float
    strength: float

class SymbiosisNetwork:
    def __init__(self):
        self.modules: Dict[str, Dict] = {}
        self.relations: List[SymbiosisRelation] = []

    def register(self, name: str, provides: List[str] = None,
                 consumes: List[str] = None):
        self.modules[name] = {"provides": set(provides or []),
                              "consumes": set(consumes or [])}

    def analyze(self) -> List[SymbiosisRelation]:
        self.relations.clear()
        names = list(self.modules.keys())
        for i, a in enumerate(names):
            for b in names[i+1:]:
                ma, mb = self.modules[a], self.modules[b]
                overlap_provide = len(ma["provides"] & mb["provides"])
                overlap_consume = len(ma["consumes"] & mb["consumes"])
                a_provides_b = len(ma["provides"] & mb["consumes"])
                b_provides_a = len(mb["provides"] & ma["consumes"])

                if a_provides_b > 0 and b_provides_a > 0:
                    rtype = RelType.MUTUAL
                    ba = min(1.0, a_provides_b * 0.3)
                    bb = min(1.0, b_provides_a * 0.3)
                elif a_provides_b > 0:
                    rtype = RelType.COMMENSAL
                    ba, bb = 0.0, min(1.0, a_provides_b * 0.3)
                elif b_provides_a > 0:
                    rtype = RelType.COMMENSAL
                    ba, bb = min(1.0, b_provides_a * 0.3), 0.0
                elif overlap_provide > 0:
                    rtype = RelType.COMPETITIVE
                    ba, bb = -0.2, -0.2
                else:
                    continue

                strength = (abs(ba) + abs(bb)) / 2
                self.relations.append(SymbiosisRelation(
                    module_a=a, module_b=b, rel_type=rtype,
                    benefit_a=ba, benefit_b=bb, strength=strength
                ))
        return self.relations

    def report(self) -> Dict:
        type_counts = {}
        for r in self.relations:
            type_counts[r.rel_type] = type_counts.get(r.rel_type, 0) + 1
        return {"modules": len(self.modules), "relations": len(self.relations),
                "types": type_counts}


def demo():
    net = SymbiosisNetwork()
    print("=== Symbiosis Network ===")
    net.register("nucleus", provides=["state", "config"], consumes=[])
    net.register("agent", provides=["actions"], consumes=["state", "config"])
    net.register("sandbox", provides=["world"], consumes=["state", "actions"])
    net.register("logger", provides=["logs"], consumes=["state", "world"])
    net.register("rogue", provides=[], consumes=["state", "config", "actions", "world"])
    net.analyze()
    report = net.report()
    print(f"  Modules: {report['modules']}, Relations: {report['relations']}")
    print(f"  Types: {report['types']}")
    for r in net.relations:
        print(f"    {r.module_a} <-> {r.module_b}: {r.rel_type} "
              f"(a={r.benefit_a:.1f}, b={r.benefit_b:.1f})")
    return report


if __name__ == "__main__":
    demo()
