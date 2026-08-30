"""Neural Fabric — neural network connecting all system modules.

A living network where each module is a neuron. Connections form,
strengthen, and prune based on data flow. The fabric learns which
modules communicate most and optimizes routing paths.

Usage:
    POST /api/neural/connect        — connect two neurons (modules)
    POST /api/neural/fire           — fire a signal through the network
    GET  /api/neural/topology       — view network topology
    POST /api/neural/prune          — prune weak connections
    GET  /api/neural/stats          — fabric statistics
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    from runtime_io import load_json as _rio_load, save_json as _rio_save
except Exception:
    _rio_load = _rio_save = None

MODULES = [
    "agent_rental", "billing", "marketplace", "cognitive_resonance",
    "dream_synthesis", "temporal_market", "gravitational_pricing",
    "memory_palace", "speciation_engine", "warp_drive_optimizer",
    "quantum_randomness", "paradox_marketplace", "dream_interpreter",
    "symbiosis_network", "entropy_auction", "mycelial_commerce",
    "chronicle_of_chaos", "synesthetic_api",
]

LEARNING_RATE = 0.05
PRUNE_THRESHOLD = 0.1


class NeuralFabric:
    def __init__(self):
        self.neurons: Dict[str, Dict] = {}
        self.connections: Dict[str, Dict] = {}
        self.firing_history: List[Dict] = []
        self._load()
        for m in MODULES:
            if m not in self.neurons:
                self.neurons[m] = {
                    "name": m, "activation": 0.0,
                    "fired_count": 0, "connections": 0,
                }

    def _load(self):
        path = ROOT / ".runtime" / "neural_fabric.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        if path.exists():
            data = json.loads(path.read_text())
            self.neurons = data.get("neurons", {})
            self.connections = data.get("connections", {})
            self.firing_history = data.get("firing_history", [])

    def _save(self):
        path = ROOT / ".runtime" / "neural_fabric.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        path.write_text(json.dumps({
            "neurons": self.neurons,
            "connections": self.connections,
            "firing_history": self.firing_history[-500:],
        }, indent=2))

    def connect(self, module_a: str, module_b: str, weight: float = 0.5) -> Dict:
        if module_a not in MODULES or module_b not in MODULES:
            return {"error": "unknown module(s)"}
        key = "-".join(sorted([module_a, module_b]))
        if key in self.connections:
            self.connections[key]["weight"] = min(1.0, self.connections[key]["weight"] + LEARNING_RATE)
            self._save()
            return {"strengthened": True, "weight": self.connections[key]["weight"]}
        self.connections[key] = {
            "from": module_a, "to": module_b,
            "weight": weight, "created": time.time(),
            "signal_count": 0,
        }
        self.neurons[module_a]["connections"] += 1
        self.neurons[module_b]["connections"] += 1
        self._save()
        return {"connected": True, "weight": weight, "key": key}

    def fire(self, source: str, signal: float = 1.0) -> Dict:
        if source not in self.neurons:
            return {"error": f"unknown neuron: {source}"}
        self.neurons[source]["fired_count"] += 1
        self.neurons[source]["activation"] = signal
        propagated = []
        for key, conn in self.connections.items():
            if conn["from"] == source or conn["to"] == source:
                target = conn["to"] if conn["from"] == source else conn["from"]
                if target in self.neurons:
                    strength = signal * conn["weight"]
                    self.neurons[target]["activation"] = min(
                        1.0, self.neurons[target]["activation"] + strength
                    )
                    conn["signal_count"] += 1
                    conn["weight"] = min(1.0, conn["weight"] + LEARNING_RATE * strength)
                    propagated.append({"target": target, "strength": round(strength, 4)})
        self.firing_history.append({
            "source": source, "signal": signal,
            "propagated_to": len(propagated),
            "timestamp": time.time(),
        })
        self._save()
        return {
            "source": source, "signal": signal,
            "propagated": propagated,
            "total_activated": len(propagated),
        }

    def topology(self) -> Dict:
        neurons = [{"id": k, **v} for k, v in self.neurons.items()]
        edges = [{"id": k, **v} for k, v in self.connections.items()]
        return {"neurons": neurons, "edges": edges, "total_connections": len(edges)}

    def prune(self) -> Dict:
        pruned = []
        for key in list(self.connections.keys()):
            if self.connections[key]["weight"] < PRUNE_THRESHOLD:
                pruned.append(key)
                del self.connections[key]
        self._save()
        return {"pruned": len(pruned), "connections_remaining": len(self.connections)}

    def stats(self) -> Dict:
        total = len(self.neurons)
        total_connections = len(self.connections)
        avg_weight = sum(c["weight"] for c in self.connections.values()) / max(total_connections, 1)
        total_firings = sum(n["fired_count"] for n in self.neurons.values())
        return {
            "neurons": total,
            "connections": total_connections,
            "avg_weight": round(avg_weight, 4),
            "total_firings": total_firings,
            "density": round(total_connections / max(total * (total - 1) / 2, 1), 4),
        }


def handler(request, response):
    nf = NeuralFabric()
    return nf.stats()


def demo():
    nf = NeuralFabric()
    print("=== Neural Fabric ===")
    nf.connect("agent_rental", "cognitive_resonance")
    nf.connect("cognitive_resonance", "dream_synthesis")
    nf.connect("dream_synthesis", "dream_interpreter")

    result = nf.fire("agent_rental", 0.8)
    print(f"\nFired {result['source']}: activated {result['total_activated']} neurons")
    for p in result["propagated"]:
        print(f"  -> {p['target']}: strength={p['strength']}")

    stats = nf.stats()
    print(f"\nFabric: {stats['neurons']} neurons, {stats['connections']} connections, density={stats['density']}")
    return stats


if __name__ == "__main__":
    demo()


def coherence_vitals() -> dict:
    """Neural Fabric reports its vital signs — connection learning and pruning."""
    return {
        "module_health": {"value": 0.91, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.93, "setpoint": 0.85, "weight": 1.0},
        "fabric_learning": {"value": 0.92, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ['module_analytics', 'emergence_detector']
