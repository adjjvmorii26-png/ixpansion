from __future__ import annotations
"""Consent Propagation — tracks how permissions flow through the system.

Like the consent-bounded cordyceps in solid-organism, every action in
the system requires consent. This module tracks how consent propagates
through the dependency chain, detecting unauthorized flows and building
a consent graph.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

@dataclass
class ConsentNode:
    name: str
    consents_to: Set[str] = field(default_factory=set)
    revoked_by: Set[str] = field(default_factory=set)
    consent_level: float = 1.0
    chain_depth: int = 0

@dataclass
class ConsentFlow:
    source: str
    target: str
    consent_level: float
    chain_position: int
    valid: bool = True

class ConsentPropagationEngine:
    def __init__(self):
        self.nodes: Dict[str, ConsentNode] = {}
        self.flows: List[ConsentFlow] = []
        self.violations: List[Dict] = []

    def register(self, name: str, consents_to: List[str] = None,
                 consent_level: float = 1.0):
        node = ConsentNode(name=name, consent_level=consent_level)
        node.consents_to = set(consents_to or [])
        self.nodes[name] = node

    def revoke(self, name: str, revoked_by: str):
        if name in self.nodes:
            self.nodes[name].revoked_by.add(revoked_by)
            self.nodes[name].consent_level = 0.0

    def propagate(self, source: str, target: str) -> ConsentFlow:
        if source not in self.nodes or target not in self.nodes:
            return ConsentFlow(source, target, 0.0, 0, valid=False)
        source_node = self.nodes[source]
        target_node = self.nodes[target]
        valid = (target in source_node.consents_to and
                 source not in target_node.revoked_by and
                 source_node.consent_level > 0)
        depth = source_node.chain_depth + 1
        level = source_node.consent_level * 0.9 if valid else 0.0
        flow = ConsentFlow(source, target, level, depth, valid)
        self.flows.append(flow)
        if not valid:
            self.violations.append({
                "source": source, "target": target,
                "reason": "unauthorized" if target not in source_node.consents_to else "revoked",
            })
        return flow

    def consent_graph(self) -> Dict:
        authorized = sum(1 for f in self.flows if f.valid)
        unauthorized = sum(1 for f in self.flows if not f.valid)
        return {
            "nodes": len(self.nodes),
            "total_flows": len(self.flows),
            "authorized": authorized,
            "unauthorized": unauthorized,
            "violations": self.violations,
            "avg_consent_level": round(
                sum(n.consent_level for n in self.nodes.values()) / max(len(self.nodes), 1), 3
            ),
        }


def demo():
    engine = ConsentPropagationEngine()
    print("=== Consent Propagation Engine ===")
    engine.register("nucleus", consents_to=["agent", "sandbox"], consent_level=1.0)
    engine.register("agent", consents_to=["observer"], consent_level=0.9)
    engine.register("sandbox", consents_to=["logger"], consent_level=0.8)
    engine.register("observer", consents_to=["logger"], consent_level=0.7)
    engine.register("logger", consents_to=[], consent_level=0.5)
    engine.propagate("nucleus", "agent")
    engine.propagate("agent", "observer")
    engine.propagate("observer", "logger")
    engine.propagate("sandbox", "logger")
    engine.propagate("logger", "nucleus")
    engine.revoke("sandbox", "nucleus")
    engine.propagate("nucleus", "sandbox")
    graph = engine.consent_graph()
    print(f"  Nodes: {graph['nodes']}, Flows: {graph['total_flows']}")
    print(f"  Authorized: {graph['authorized']}, Unauthorized: {graph['unauthorized']}")
    print(f"  Violations: {graph['violations']}")
    return graph


if __name__ == "__main__":
    demo()
