"""Resonance Cascade — chain reactions of amplification across the system.

A small event can trigger a cascade when it hits the right resonance
frequencies. The cascade engine models how events amplify as they
bounce between resonant nodes, creating echo chambers, feedback loops,
and emergent phenomena that dwarf the original trigger.
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


class ResonanceNode:
    def __init__(self, name: str, frequency: float = 1.0, dampening: float = 0.1):
        self.name = name
        self.frequency = frequency
        self.dampening = dampening
        self.energy = 0.0
        self.total_energy_received = 0.0
        self.trigger_count = 0

    def receive(self, energy: float, source_freq: float) -> Dict[str, Any]:
        resonance = 1.0 - min(abs(self.frequency - source_freq) / 10.0, 1.0)
        amplified = energy * (1.0 + resonance) * (1.0 - self.dampening)
        self.energy += amplified
        self.total_energy_received += amplified
        self.trigger_count += 1
        return {"amplified": round(amplified, 4), "resonance": round(resonance, 4)}

    def discharge(self) -> float:
        energy = self.energy
        self.energy = 0.0
        return energy

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "frequency": round(self.frequency, 3),
            "energy": round(self.energy, 4),
            "total_received": round(self.total_energy_received, 4),
            "triggers": self.trigger_count,
        }


class ResonanceCascade:
    def __init__(self):
        self.nodes: Dict[str, ResonanceNode] = {}
        self.cascades: List[Dict[str, Any]] = []
        self.total_energy_circulated = 0.0

    def add_node(self, name: str, frequency: float = None, dampening: float = None) -> Dict[str, Any]:
        node = ResonanceNode(
            name,
            frequency or random.uniform(0.5, 5.0),
            dampening or random.uniform(0.05, 0.3),
        )
        self.nodes[name] = node
        return {"node": node.to_dict()}

    def trigger(self, source: str, energy: float = 1.0) -> Dict[str, Any]:
        """Trigger a cascade from a source node."""
        if source not in self.nodes:
            return {"error": "node not found"}
        cascade = {
            "source": source,
            "initial_energy": energy,
            "steps": [],
            "total_amplified": 0.0,
        }
        visited: Set[str] = set()
        queue = [(source, energy)]
        for _ in range(10):
            next_queue = []
            for node_name, incoming_energy in queue:
                if node_name in visited:
                    continue
                visited.add(node_name)
                node = self.nodes[node_name]
                result = node.receive(incoming_energy, self.nodes[source].frequency)
                self.total_energy_circulated += result["amplified"]
                cascade["steps"].append({
                    "node": node_name,
                    "received": round(incoming_energy, 4),
                    **result,
                })
                cascade["total_amplified"] += result["amplified"]
                if result["resonance"] > 0.3:
                    for other_name, other_node in self.nodes.items():
                        if other_name not in visited:
                            next_queue.append((other_name, result["amplified"] * 0.5))
            queue = next_queue
            if not queue:
                break
        self.cascades.append(cascade)
        return cascade

    def cascade_history(self) -> List[Dict[str, Any]]:
        return [
            {"source": c["source"], "total_amplified": round(c["total_amplified"], 4), "steps": len(c["steps"])}
            for c in self.cascades
        ]

    def strongest_resonance(self) -> Dict[str, Any]:
        max_res = 0
        pair = ("", "")
        nodes = list(self.nodes.values())
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                res = 1.0 - min(abs(nodes[i].frequency - nodes[j].frequency) / 10.0, 1.0)
                if res > max_res:
                    max_res = res
                    pair = (nodes[i].name, nodes[j].name)
        return {"pair": pair, "resonance": round(max_res, 4)}

    def stats(self) -> Dict[str, Any]:
        return {
            "total_nodes": len(self.nodes),
            "total_cascades": len(self.cascades),
            "total_energy_circulated": round(self.total_energy_circulated, 4),
            "avg_node_energy": round(
                sum(n.total_energy_received for n in self.nodes.values()) /
                max(len(self.nodes), 1), 4
            ),
        }


_cascade = ResonanceCascade()


def resonance_cascade_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "add_node":
        return _cascade.add_node(
            payload.get("name", f"node_{random.randint(100,999)}"),
            payload.get("frequency"),
            payload.get("dampening"),
        )
    elif action == "trigger":
        return _cascade.trigger(
            payload.get("source", ""),
            payload.get("energy", 1.0),
        )
    elif action == "history":
        return {"cascades": _cascade.cascade_history()}
    elif action == "strongest":
        return _cascade.strongest_resonance()
    return {"status": "active", **_cascade.stats()}


handler = resonance_cascade_handler


def coherence_vitals() -> dict:
    """resonance_cascade reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance_cascade_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['neural_pathway', 'echoes_of_tomorrow', 'universal_compass']

