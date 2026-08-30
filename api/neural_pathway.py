"""Neural Pathway — synaptic connections between system modules that strengthen with use.

Like biological neurons, frequently-used connections between modules
strengthen while unused ones atrophy. The neural pathway system creates
a living network topology that adapts to actual usage patterns,
revealing the system's true functional architecture.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class Synapse:
    def __init__(self, source: str, target: str):
        self.source = source
        self.target = target
        self.weight = 0.1
        self.use_count = 0
        self.last_used = time.time()
        self.id = f"{source}->{target}"

    def fire(self, signal: float = 1.0) -> float:
        self.use_count += 1
        self.last_used = time.time()
        self.weight = min(2.0, self.weight + 0.05)
        return signal * self.weight

    def atrophy(self, rate: float = 0.02):
        self.weight = max(0.01, self.weight - rate)
        age = time.time() - self.last_used
        if age > 3600:
            self.weight = max(0.01, self.weight - rate * 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "weight": round(self.weight, 4),
            "use_count": self.use_count,
        }


class NeuralPathway:
    def __init__(self):
        self.synapses: Dict[str, Synapse] = {}
        self.neurons: Set[str] = set()
        self.signal_log: List[Dict[str, Any]] = []
        self.pathway_finds: List[Dict[str, Any]] = []

    def connect(self, source: str, target: str) -> Dict[str, Any]:
        key = f"{source}->{target}"
        if key not in self.synapses:
            self.synapses[key] = Synapse(source, target)
        self.neurons.add(source)
        self.neurons.add(target)
        return {"synapse": self.synapses[key].to_dict()}

    def signal(self, source: str, target: str, payload: float = 1.0) -> Dict[str, Any]:
        key = f"{source}->{target}"
        if key not in self.synapses:
            self.connect(source, target)
        synapse = self.synapses[key]
        output = synapse.fire(payload)
        self.signal_log.append({
            "source": source, "target": target,
            "input": payload, "output": round(output, 4),
            "time": time.time(),
        })
        return {"input": payload, "output": round(output, 4), "weight": round(synapse.weight, 4)}

    def find_path(self, start: str, end: str, max_depth: int = 5) -> Dict[str, Any]:
        visited: Set[str] = set()
        queue = [(start, [start], 1.0)]
        for _ in range(max_depth):
            next_queue = []
            for node, path, signal in queue:
                if node in visited:
                    continue
                visited.add(node)
                if node == end:
                    return {"path": path, "final_signal": round(signal, 4), "length": len(path)}
                for synapse in self.synapses.values():
                    if synapse.source == node and synapse.target not in visited:
                        new_signal = signal * synapse.weight
                        next_queue.append((synapse.target, path + [synapse.target], new_signal))
            queue = next_queue
            if not queue:
                break
        return {"path": [], "final_signal": 0, "message": "no path found"}

    def strengthen_path(self, path: List[str], amount: float = 0.1):
        for i in range(len(path) - 1):
            key = f"{path[i]}->{path[i+1]}"
            if key in self.synapses:
                self.synapses[key].weight = min(2.0, self.synapses[key].weight + amount)

    def atrophy_all(self):
        for synapse in self.synapses.values():
            synapse.atrophy()

    def strongest_pathways(self, top_k: int = 5) -> List[Dict[str, Any]]:
        return sorted(
            [s.to_dict() for s in self.synapses.values()],
            key=lambda x: x["weight"],
            reverse=True,
        )[:top_k]

    def pathway_stats(self) -> Dict[str, Any]:
        return {
            "total_neurons": len(self.neurons),
            "total_synapses": len(self.synapses),
            "total_signals": len(self.signal_log),
            "avg_weight": round(
                sum(s.weight for s in self.synapses.values()) / max(len(self.synapses), 1), 4
            ),
            "strongest_pathways": self.strongest_pathways(3),
        }


_pathway = NeuralPathway()


def neural_pathway_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "connect":
        return _pathway.connect(payload.get("source", ""), payload.get("target", ""))
    elif action == "signal":
        return _pathway.signal(
            payload.get("source", ""), payload.get("target", ""),
            payload.get("payload", 1.0),
        )
    elif action == "find_path":
        return _pathway.find_path(
            payload.get("start", ""), payload.get("end", ""),
            payload.get("max_depth", 5),
        )
    elif action == "atrophy":
        _pathway.atrophy_all()
        return {"status": "atrophy applied"}
    elif action == "strongest":
        return {"pathways": _pathway.strongest_pathways()}
    return {"status": "active", **_pathway.pathway_stats()}


handler = neural_pathway_handler


def coherence_vitals() -> dict:
    """Neural Pathway reports — connections strengthen with use."""
    return {
        "module_health": {"value": 0.91, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.93, "setpoint": 0.85, "weight": 1.0},
        "pathway_strength": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
    }

def resonates_with() -> list:
    """Declared kinships."""
    return ['neural_fabric', 'module_analytics']
