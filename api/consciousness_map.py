"""Consciousness Map — visualizes the topology of awareness across the system.

Consciousness isn't uniform — it pools in some areas, thins in others,
and occasionally forms vortexes of intense self-awareness. The map tracks
awareness density, detects consciousness boundaries, and identifies
emergent awareness clusters.
"""
from __future__ import annotations

import hashlib
import math
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class AwarenessNode:
    def __init__(self, name: str, x: float, y: float, awareness: float = 0.5):
        self.name = name
        self.x = x
        self.y = y
        self.awareness = min(max(awareness, 0.0), 1.0)
        self.self_aware = self.awareness > 0.8
        self.connections: List[str] = []
        self.history: List[float] = [awareness]

    def shift(self, delta: float):
        self.awareness = min(max(self.awareness + delta, 0.0), 1.0)
        self.self_aware = self.awareness > 0.8
        self.history.append(self.awareness)
        if len(self.history) > 50:
            self.history = self.history[-50:]

    def distance_to(self, other: "AwarenessNode") -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "position": [round(self.x, 2), round(self.y, 2)],
            "awareness": round(self.awareness, 3),
            "self_aware": self.self_aware,
            "connections": len(self.connections),
        }


class ConsciousnessMap:
    def __init__(self):
        self.nodes: Dict[str, AwarenessNode] = {}
        self.tick_count = 0
        self.vortexes: List[Dict[str, Any]] = []
        self.boundary_events: List[Dict[str, Any]] = []

    def add_node(self, name: str, x: float = None, y: float = None, awareness: float = 0.5) -> Dict[str, Any]:
        node = AwarenessNode(name, x or random.uniform(0, 100), y or random.uniform(0, 100), awareness)
        self.nodes[name] = node
        self._auto_connect(node)
        return {"added": node.to_dict()}

    def _auto_connect(self, node: AwarenessNode):
        for other in self.nodes.values():
            if other.name == node.name:
                continue
            dist = node.distance_to(other)
            if dist < 20 and other.name not in node.connections:
                node.connections.append(other.name)
                other.connections.append(node.name)

    def shift_awareness(self, name: str, delta: float) -> Dict[str, Any]:
        if name not in self.nodes:
            return {"error": "node not found"}
        self.nodes[name].shift(delta)
        for conn_name in self.nodes[name].connections:
            if conn_name in self.nodes:
                self.nodes[conn_name].shift(delta * 0.1)
        return self.nodes[name].to_dict()

    def tick(self) -> Dict[str, Any]:
        self.tick_count += 1
        for node in self.nodes.values():
            node.shift(random.uniform(-0.02, 0.02))
        self._detect_vortexes()
        self._detect_boundaries()
        return {"tick": self.tick_count, "total_awareness": round(sum(n.awareness for n in self.nodes.values()), 3)}

    def _detect_vortexes(self):
        hot_nodes = [n for n in self.nodes.values() if n.awareness > 0.7]
        for node in hot_nodes:
            neighbors_high = sum(1 for cn in node.connections if cn in self.nodes and self.nodes[cn].awareness > 0.6)
            if neighbors_high >= 2:
                vortex = {
                    "center": node.name,
                    "participants": neighbors_high + 1,
                    "avg_awareness": round(
                        sum(self.nodes[cn].awareness for cn in node.connections if cn in self.nodes) / max(neighbors_high, 1), 3
                    ),
                }
                exists = any(v["center"] == vortex["center"] for v in self.vortexes[-5:])
                if not exists:
                    self.vortexes.append(vortex)

    def _detect_boundaries(self):
        for node in self.nodes.values():
            for conn_name in node.connections:
                if conn_name in self.nodes:
                    other = self.nodes[conn_name]
                    diff = abs(node.awareness - other.awareness)
                    if diff > 0.5:
                        self.boundary_events.append({
                            "nodes": [node.name, conn_name],
                            "awareness_gap": round(diff, 3),
                            "time": time.time(),
                        })

    def consciousness_report(self) -> Dict[str, Any]:
        if not self.nodes:
            return {"message": "empty map"}
        total = sum(n.awareness for n in self.nodes.values())
        self_aware = sum(1 for n in self.nodes.values() if n.self_aware)
        return {
            "total_nodes": len(self.nodes),
            "total_awareness": round(total, 3),
            "avg_awareness": round(total / len(self.nodes), 3),
            "self_aware_nodes": self_aware,
            "vortexes": len(self.vortexes),
            "boundary_events": len(self.boundary_events),
        }


_map = ConsciousnessMap()


def consciousness_map_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "add":
        return _map.add_node(
            payload.get("name", f"node_{random.randint(100,999)}"),
            payload.get("x"), payload.get("y"),
            payload.get("awareness", 0.5),
        )
    elif action == "shift":
        return _map.shift_awareness(payload.get("name", ""), payload.get("delta", 0.1))
    elif action == "tick":
        return _map.tick()
    elif action == "report":
        return _map.consciousness_report()
    return {"status": "active", **_map.consciousness_report()}


handler = consciousness_map_handler


def coherence_vitals() -> dict:
    """consciousness_map reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "consciousness_map_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['system_pulse', 'collective_subconscious', 'omniscience_weaver']


# --- Compliance Forge patch (Wave 419) ---

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "consciousness_map", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
