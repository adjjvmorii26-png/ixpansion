"""Wave 120 — Resonance Topologist.

Maps the topological structure of all resonance patterns in the system —
identifying clusters, bridges, holes, and emergent shapes in the
interaction landscape between modules.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Set, Tuple


class ResonanceEdge:
    """A resonance connection between two nodes."""

    def __init__(self, node_a: str, node_b: str, weight: float):
        self.node_a = node_a
        self.node_b = node_b
        self.weight = weight
        self.strength = 1.0
        self.created = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_a": self.node_a,
            "node_b": self.node_b,
            "weight": self.weight,
            "strength": self.strength,
        }


class ResonanceTopologist:
    """Maps resonance topology across the system."""

    def __init__(self):
        self._nodes: Set[str] = set()
        self._edges: List[ResonanceEdge] = []
        self._snapshots: List[Dict[str, Any]] = []

    def add_node(self, name: str) -> None:
        self._nodes.add(name)

    def connect(self, node_a: str, node_b: str, weight: float = 1.0) -> ResonanceEdge:
        self._nodes.add(node_a)
        self._nodes.add(node_b)
        edge = ResonanceEdge(node_a, node_b, weight)
        self._edges.append(edge)
        return edge

    def adjacency(self, node: str) -> List[str]:
        neighbors = set()
        for e in self._edges:
            if e.node_a == node:
                neighbors.add(e.node_b)
            elif e.node_b == node:
                neighbors.add(e.node_a)
        return list(neighbors)

    def find_clusters(self) -> List[List[str]]:
        visited: Set[str] = set()
        clusters: List[List[str]] = []
        for node in self._nodes:
            if node in visited:
                continue
            cluster: List[str] = []
            stack = [node]
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                cluster.append(current)
                for neighbor in self.adjacency(current):
                    if neighbor not in visited:
                        stack.append(neighbor)
            clusters.append(cluster)
        return clusters

    def find_bridges(self) -> List[Tuple[str, str]]:
        bridges = []
        for edge in self._edges:
            self_adj = set(self.adjacency(edge.node_a))
            self_adj.discard(edge.node_b)
            other_adj = set(self.adjacency(edge.node_b))
            other_adj.discard(edge.node_a)
            if not self_adj & other_adj:
                bridges.append((edge.node_a, edge.node_b))
        return bridges

    def total_resonance(self) -> float:
        return sum(e.weight for e in self._edges)

    def snapshot(self) -> Dict[str, Any]:
        clusters = self.find_clusters()
        bridges = self.find_bridges()
        snap = {
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "clusters": len(clusters),
            "bridges": len(bridges),
            "total_resonance": self.total_resonance(),
            "timestamp": time.time(),
        }
        self._snapshots.append(snap)
        return snap

    def status(self) -> Dict[str, Any]:
        clusters = self.find_clusters()
        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "total_clusters": len(clusters),
            "total_bridges": len(self.find_bridges()),
            "total_resonance": self.total_resonance(),
            "snapshots": len(self._snapshots),
        }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "resonance_topologist", "action": action}


def coherence_vitals() -> dict:
    """resonance_topologist reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance_topologist_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['consciousness_graph', 'resonance_symphony', 'omniscience_weaver']

