"""Knowledge Graph — maps relationships between all concepts in the system.

Every concept, entity, and relationship in the system is a node or edge
in a vast knowledge graph. The graph reveals hidden connections, identifies
knowledge gaps, and suggests new research directions based on structural
 holes in the graph.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class KGNode:
    def __init__(self, name: str, node_type: str = "concept", weight: float = 1.0):
        self.name = name
        self.node_type = node_type
        self.weight = weight
        self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "type": self.node_type, "weight": round(self.weight, 3)}


class KnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, KGNode] = {}
        self.edges: Dict[str, Dict[str, Any]] = {}
        self.adjacency: Dict[str, Set[str]] = {}

    def add_node(self, name: str, node_type: str = "concept", weight: float = 1.0) -> Dict[str, Any]:
        node = KGNode(name, node_type, weight)
        self.nodes[name] = node
        self.adjacency.setdefault(name, set())
        return {"added": node.to_dict()}

    def add_edge(self, source: str, target: str, relation: str = "related", weight: float = 1.0) -> Dict[str, Any]:
        if source not in self.nodes:
            self.add_node(source)
        if target not in self.nodes:
            self.add_node(target)
        edge_key = f"{source}->{target}"
        self.edges[edge_key] = {"relation": relation, "weight": weight}
        self.adjacency[source].add(target)
        self.adjacency[target].add(source)
        return {"edge": edge_key, "relation": relation}

    def neighbors(self, node: str) -> List[Dict[str, Any]]:
        if node not in self.adjacency:
            return []
        return [self.nodes[n].to_dict() for n in self.adjacency[node] if n in self.nodes]

    def find_path(self, start: str, end: str, max_depth: int = 5) -> Dict[str, Any]:
        if start not in self.nodes or end not in self.nodes:
            return {"error": "node not found"}
        visited: Set[str] = set()
        queue = [(start, [start])]
        for _ in range(max_depth):
            next_queue = []
            for node, path in queue:
                if node in visited:
                    continue
                visited.add(node)
                if node == end:
                    return {"path": path, "length": len(path)}
                for neighbor in self.adjacency.get(node, set()):
                    if neighbor not in visited:
                        next_queue.append((neighbor, path + [neighbor]))
            queue = next_queue
        return {"path": [], "message": "no path found"}

    def knowledge_gaps(self) -> List[Dict[str, Any]]:
        disconnected = []
        for name in self.nodes:
            if len(self.adjacency.get(name, set())) == 0:
                disconnected.append({"node": name, "status": "isolated"})
        low_connectivity = []
        for name, neighbors in self.adjacency.items():
            if 0 < len(neighbors) <= 1 and len(self.nodes) > 5:
                low_connectivity.append({"node": name, "connections": len(neighbors), "status": "underconnected"})
        return disconnected + low_connectivity[:10]

    def graph_stats(self) -> Dict[str, Any]:
        type_counts: Dict[str, int] = {}
        for node in self.nodes.values():
            type_counts[node.node_type] = type_counts.get(node.node_type, 0) + 1
        avg_degree = sum(len(n) for n in self.adjacency.values()) / max(len(self.nodes), 1)
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "type_distribution": type_counts,
            "avg_degree": round(avg_degree, 2),
            "knowledge_gaps": len(self.knowledge_gaps()),
        }


_graph = KnowledgeGraph()


def knowledge_graph_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "add_node":
        return _graph.add_node(
            payload.get("name", f"concept_{random.randint(100,999)}"),
            payload.get("node_type", "concept"),
            payload.get("weight", 1.0),
        )
    elif action == "add_edge":
        return _graph.add_edge(
            payload.get("source", ""), payload.get("target", ""),
            payload.get("relation", "related"), payload.get("weight", 1.0),
        )
    elif action == "neighbors":
        return {"neighbors": _graph.neighbors(payload.get("node", ""))}
    elif action == "path":
        return _graph.find_path(payload.get("start", ""), payload.get("end", ""))
    elif action == "gaps":
        return {"gaps": _graph.knowledge_gaps()}
    return {"status": "active", **_graph.graph_stats()}
