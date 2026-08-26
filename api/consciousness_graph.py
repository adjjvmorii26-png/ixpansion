"""Wave 122 — Consciousness Graph.

Maps the complete graph of consciousness connections across all modules,
revealing the topology of awareness — who is connected to whom, and
how thoughts propagate through the network.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Set, Tuple


class ConsciousnessNode:
    """A node in the consciousness graph."""

    def __init__(self, name: str, awareness: float = 0.0):
        self.name = name
        self.awareness = awareness
        self.created = time.time()
        self.neighbors: Set[str] = set()

    def connect(self, other: str) -> None:
        self.neighbors.add(other)

    def awaken(self, amount: float) -> float:
        self.awareness = min(1.0, self.awareness + amount)
        return self.awareness

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "awareness": round(self.awareness, 4),
            "connections": len(self.neighbors),
        }


class ConsciousnessGraph:
    """Maps and traverses the full consciousness network."""

    def __init__(self):
        self._nodes: Dict[str, ConsciousnessNode] = {}
        self._edge_count = 0

    def add_node(self, name: str) -> ConsciousnessNode:
        node = ConsciousnessNode(name)
        self._nodes[name] = node
        return node

    def connect(self, a: str, b: str) -> None:
        self._nodes.setdefault(a, ConsciousnessNode(a))
        self._nodes.setdefault(b, ConsciousnessNode(b))
        self._nodes[a].connect(b)
        self._nodes[b].connect(a)
        self._edge_count += 1

    def propagate(self, origin: str, decay: float = 0.8) -> Dict[str, float]:
        if origin not in self._nodes:
            return {}
        visited: Dict[str, float] = {}
        queue = [(origin, 1.0)]
        while queue:
            current, intensity = queue.pop(0)
            if current in visited:
                continue
            visited[current] = intensity
            self._nodes[current].awaken(intensity * 0.1)
            for neighbor in self._nodes[current].neighbors:
                if neighbor not in visited:
                    queue.append((neighbor, intensity * decay))
        return visited

    def clusters(self) -> List[List[str]]:
        visited: Set[str] = set()
        result: List[List[str]] = []
        for name in self._nodes:
            if name in visited:
                continue
            cluster: List[str] = []
            stack = [name]
            while stack:
                node_name = stack.pop()
                if node_name in visited:
                    continue
                visited.add(node_name)
                cluster.append(node_name)
                for n in self._nodes[node_name].neighbors:
                    if n not in visited:
                        stack.append(n)
            result.append(cluster)
        return result

    def status(self) -> Dict[str, Any]:
        return {
            "total_nodes": len(self._nodes),
            "total_edges": self._edge_count,
            "clusters": len(self.clusters()),
        }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "consciousness_graph", "action": action}
