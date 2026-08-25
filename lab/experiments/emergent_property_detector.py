from __future__ import annotations
"""Emergent Property Detector — finds behaviors that arise from component interactions.

Like how wetness emerges from H2O molecules (none of which are individually
"wet"), some system behaviors emerge from component interactions. This module
detects properties that aren't present in any individual module but appear
when modules interact.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

@dataclass
class ComponentProperty:
    name: str
    properties: Set[str]
    interactions: int = 0

@dataclass
class EmergentProperty:
    name: str
    components: List[str]
    confidence: float
    evidence: List[str]
    category: str

class EmergentPropertyDetector:
    def __init__(self):
        self.components: Dict[str, ComponentProperty] = {}
        self.interactions: List[Tuple[str, str, str]] = []
        self.emergent: List[EmergentProperty] = []

    def register(self, name: str, properties: List[str]):
        self.components[name] = ComponentProperty(
            name=name, properties=set(properties)
        )

    def record_interaction(self, comp_a: str, comp_b: str, result: str):
        self.interactions.append((comp_a, comp_b, result))

    def detect(self) -> List[EmergentProperty]:
        self.emergent.clear()
        all_component_props = set()
        for comp in self.components.values():
            all_component_props.update(comp.properties)

        interaction_results = {}
        for a, b, result in self.interactions:
            key = frozenset([a, b])
            if key not in interaction_results:
                interaction_results[key] = set()
            interaction_results[key].add(result)

        for pair, results in interaction_results.items():
            emergent_props = results - all_component_props
            for prop in emergent_props:
                components = list(pair)
                confidence = min(1.0, len(results) / 3.0)
                category = "behavioral" if any(
                    k in prop.lower() for k in ["flow", "cascade", "propagat"]
                ) else "structural"
                self.emergent.append(EmergentProperty(
                    name=prop, components=components,
                    confidence=round(confidence, 3),
                    evidence=list(results),
                    category=category,
                ))
        return self.emergent

    def report(self) -> Dict:
        return {
            "components": len(self.components),
            "interactions": len(self.interactions),
            "emergent_properties": len(self.emergent),
            "categories": {
                cat: sum(1 for e in self.emergent if e.category == cat)
                for cat in set(e.category for e in self.emergent) if self.emergent
            },
            "properties": [
                {"name": e.name, "components": e.components,
                 "confidence": e.confidence, "category": e.category}
                for e in self.emergent
            ],
        }


def demo():
    detector = EmergentPropertyDetector()
    print("=== Emergent Property Detector ===")
    detector.register("agent", ["decision_making", "observation"])
    detector.register("sandbox", ["state_management", "event_processing"])
    detector.register("protocol", ["message_encoding", "routing"])
    detector.record_interaction("agent", "sandbox", "adaptive_behavior")
    detector.record_interaction("agent", "sandbox", "feedback_loop")
    detector.record_interaction("agent", "sandbox", "emergent_strategy")
    detector.record_interaction("sandbox", "protocol", "event_cascade")
    detector.record_interaction("sandbox", "protocol", "self_organization")
    detector.record_interaction("agent", "protocol", "distributed_consensus")
    detector.record_interaction("agent", "protocol", "collective_intelligence")
    detector.record_interaction("agent", "protocol", "swarm_emergence")
    emergent = detector.detect()
    print(f"  Emergent properties found: {len(emergent)}")
    for e in emergent:
        print(f"    {e.name}: {e.components} (confidence={e.confidence}, "
              f"category={e.category})")
    report = detector.report()
    print(f"\n  Categories: {report['categories']}")
    return report


if __name__ == "__main__":
    demo()
