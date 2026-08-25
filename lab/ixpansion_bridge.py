"""Ixpansion Bridge — Connects glitch, expansion, and mesh subsystems.

Provides unified access to the ixpansion engine's core capabilities:
mutation application, conflict resolution, mesh topology, and glitch detection.
"""
from __future__ import annotations
import hashlib
import random
import time
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class MutationApplier:
    def __init__(self):
        self.applied: list[dict] = []

    def apply(self, state: dict, field: str, operation: str, value: Any) -> dict:
        current = state.get(field)
        if operation == "set":
            state[field] = value
        elif operation == "add":
            state[field] = (current or 0) + value
        elif operation == "multiply":
            state[field] = (current or 0) * value
        else:
            if not isinstance(current, list):
                current = []
            current.append(value)
            state[field] = current
        mutation = {"field": field, "operation": operation, "value": value, "result": state.get(field)}
        self.applied.append(mutation)
        return state


class ConflictResolver:
    def __init__(self):
        self.resolutions: list[dict] = []

    def resolve(self, candidates: list[Any]) -> dict:
        if not candidates:
            return {"error": "no candidates"}
        counts = Counter(str(c) for c in candidates)
        winner, votes = counts.most_common(1)[0]
        result = {"resolved": winner, "votes": votes, "quorum": votes > len(candidates) / 2}
        self.resolutions.append(result)
        return result


class MeshTopology:
    def __init__(self, seed=42):
        self.seed = seed
        self.nodes: dict[str, dict] = {}
        self.connections: list[tuple[str, str]] = []
        self.strategy = "star"

    def add_node(self, name: str, role: str = "worker"):
        self.nodes[name] = {"role": role, "connections": 0, "messages_sent": 0}

    def connect(self, a: str, b: str):
        if a in self.nodes and b in self.nodes:
            self.connections.append((a, b))
            self.nodes[a]["connections"] += 1
            self.nodes[b]["connections"] += 1

    def auto_connect(self, strategy="star"):
        self.strategy = strategy
        names = list(self.nodes.keys())
        if not names:
            return
        if strategy == "star":
            hub = names[0]
            for n in names[1:]:
                self.connect(hub, n)
        elif strategy == "ring":
            for i in range(len(names)):
                self.connect(names[i], names[(i + 1) % len(names)])
        elif strategy == "chaotic":
            rng = random.Random(self.seed)
            for _ in range(len(names)):
                a, b = rng.sample(names, 2)
                self.connect(a, b)

    def send_message(self, source: str, target: str):
        if source in self.nodes:
            self.nodes[source]["messages_sent"] += 1

    def report(self) -> dict:
        return {
            "nodes": len(self.nodes), "connections": len(self.connections),
            "strategy": self.strategy,
            "top_nodes": sorted(
                [{"name": n, **d} for n, d in self.nodes.items()],
                key=lambda x: x["connections"], reverse=True
            )[:5],
        }


class GlitchDetector:
    def __init__(self):
        self.anomalies: list[dict] = []

    def scan(self, state: dict) -> list[dict]:
        detected = []
        for key, value in state.items():
            if isinstance(value, float) and (value > 10 or value < -10):
                detected.append({"type": "extreme_value", "field": key, "value": value})
            elif isinstance(value, str) and len(value) > 200:
                detected.append({"type": "oversized_string", "field": key, "length": len(value)})
            elif isinstance(value, list) and len(value) > 100:
                detected.append({"type": "oversized_list", "field": key, "length": len(value)})
        self.anomalies.extend(detected)
        return detected


class IxpansionBridge:
    def __init__(self, seed=42):
        self.seed = seed
        self.mutation_applier = MutationApplier()
        self.conflict_resolver = ConflictResolver()
        self.mesh = MeshTopology(seed)
        self.glitch_detector = GlitchDetector()
        self.state: dict[str, Any] = {"epoch": 0, "entropy": 0.0, "cohesion": 1.0}

    def tick(self) -> dict:
        self.state["epoch"] = self.state.get("epoch", 0) + 1
        self.state["entropy"] += random.Random(self.state["epoch"]).uniform(-0.02, 0.03)
        self.state["entropy"] = max(0, min(1, self.state["entropy"]))
        mutations = random.Random(self.state["epoch"]).randint(0, 3)
        for _ in range(mutations):
            field = random.Random(self.state["epoch"]).choice(["entropy", "cohesion"])
            op = random.Random(self.state["epoch"]).choice(["add", "multiply"])
            val = random.Random(self.state["epoch"]).uniform(-0.01, 0.01)
            self.state = self.mutation_applier.apply(self.state, field, op, val)
        glitches = self.glitch_detector.scan(self.state)
        return {
            "epoch": self.state["epoch"],
            "state": {k: round(v, 4) if isinstance(v, float) else v for k, v in self.state.items()},
            "mutations": mutations,
            "glitches": len(glitches),
        }

    def simulate(self, ticks=10) -> dict:
        results = [self.tick() for _ in range(ticks)]
        return {
            "ticks": ticks,
            "final_state": self.state,
            "total_mutations": len(self.mutation_applier.applied),
            "total_glitches": len(self.glitch_detector.anomalies),
            "mesh": self.mesh.report(),
        }

    def report(self) -> dict:
        return {
            "bridge": "ixpansion_bridge",
            "mutations_applied": len(self.mutation_applier.applied),
            "conflicts_resolved": len(self.conflict_resolver.resolutions),
            "mesh_nodes": len(self.mesh.nodes),
            "glitches_detected": len(self.glitch_detector.anomalies),
        }


def demo():
    bridge = IxpansionBridge(seed=42)
    bridge.mesh.add_node("hub", "coordinator")
    for i in range(5):
        bridge.mesh.add_node(f"worker_{i}", "worker")
    bridge.mesh.auto_connect("star")
    sim = bridge.simulate(ticks=15)
    return {"simulation": sim, "report": bridge.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
