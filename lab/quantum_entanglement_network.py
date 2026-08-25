"""Quantum Entanglement Network — Connects distant modules via quantum links.

Creates a network where modules can be entangled regardless of distance,
enabling instant correlation across the entire codebase.
"""
from __future__ import annotations
import hashlib
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class QuantumNode:
    def __init__(self, name: str, subsystem: str):
        self.name = name
        self.subsystem = subsystem
        self.entangled_with: list[str] = []
        self.measurement_count = 0
        self.state = "superposition"

    def measure(self) -> str:
        self.measurement_count += 1
        self.state = "collapsed"
        return self.state

    def to_dict(self) -> dict:
        return {
            "name": self.name, "subsystem": self.subsystem,
            "entangled": len(self.entangled_with),
            "measurements": self.measurement_count,
            "state": self.state,
        }


class QuantumEntanglementNetwork:
    def __init__(self, seed=42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.nodes: dict[str, QuantumNode] = {}
        self.entanglements: list[dict] = []
        self.bell_states = ["phi+", "phi-", "psi+", "psi-"]

    def add_node(self, name: str, subsystem: str):
        self.nodes[name] = QuantumNode(name, subsystem)

    def entangle(self, a: str, b: str) -> dict:
        if a not in self.nodes or b not in self.nodes:
            return {"error": "node not found"}
        strength = self.rng.uniform(0.5, 1.0)
        bell_state = self.rng.choice(self.bell_states)
        self.nodes[a].entangled_with.append(b)
        self.nodes[b].entangled_with.append(a)
        entanglement = {"pair": (a, b), "strength": round(strength, 4), "bell_state": bell_state}
        self.entanglements.append(entanglement)
        return entanglement

    def measure_pair(self, a: str, b: str) -> dict:
        if a not in self.nodes or b not in self.nodes:
            return {"error": "node not found"}
        self.nodes[a].measure()
        self.nodes[b].measure()
        correlated = self.rng.random() > 0.3
        return {
            "a": self.nodes[a].to_dict(),
            "b": self.nodes[b].to_dict(),
            "correlated": correlated,
        }

    def auto_entangle(self, probability: float = 0.3):
        names = list(self.nodes.keys())
        for i, a in enumerate(names):
            for b in names[i+1:]:
                if self.rng.random() < probability:
                    self.entangle(a, b)

    def report(self) -> dict:
        entangled_nodes = sum(1 for n in self.nodes.values() if n.entangled_with)
        return {
            "network": "quantum_entanglement_network",
            "nodes": len(self.nodes),
            "entanglements": len(self.entanglements),
            "entangled_nodes": entangled_nodes,
            "bell_state_distribution": {
                bs: sum(1 for e in self.entanglements if e["bell_state"] == bs)
                for bs in self.bell_states
            },
            "top_nodes": sorted(
                [n.to_dict() for n in self.nodes.values()],
                key=lambda x: x["entangled"], reverse=True
            )[:5],
        }


def demo():
    net = QuantumEntanglementNetwork(seed=42)
    for base_name, base_path in [("api", ROOT / "api"), ("lab", ROOT / "lab" / "experiments"), ("bridges", ROOT / "bridges")]:
        if base_path.exists():
            for py in list(base_path.glob("*.py"))[:6]:
                if not py.name.startswith("_") and not py.name.startswith("test_"):
                    net.add_node(py.stem, base_name)
    net.auto_entangle(probability=0.2)
    if len(net.nodes) >= 2:
        names = list(net.nodes.keys())
        net.measure_pair(names[0], names[1])
    return net.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
