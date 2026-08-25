from __future__ import annotations
"""Dimensional Fold — folds module dependency graph into higher dimensions.

By projecting the flat dependency graph into higher dimensions (3D, 4D),
hidden shortcuts and cluster structures become visible. Modules that
appear distant in 2D may be adjacent in higher dimensions.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class DimensionalNode:
    name: str
    coords: List[float] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)
    cluster: int = -1
    dimension: int = 2

    def distance_to(self, other: "DimensionalNode") -> float:
        max_len = max(len(self.coords), len(other.coords))
        a = self.coords + [0.0] * (max_len - len(self.coords))
        b = other.coords + [0.0] * (max_len - len(other.coords))
        return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(max_len)))

@dataclass
class FoldResult:
    original_edges: int
    folded_edges: int
    hidden_shortcuts: List[Tuple[str, str, float]]
    cluster_count: int
    avg_distance_reduction: float

class DimensionalFolder:
    def __init__(self, target_dim: int = 3):
        self.target_dim = target_dim
        self.nodes: Dict[str, DimensionalNode] = {}
        self.edges: List[Tuple[str, str]] = []

    def add_node(self, name: str) -> DimensionalNode:
        coords = [0.0] * self.target_dim
        node = DimensionalNode(name=name, coords=coords, dimension=self.target_dim)
        self.nodes[name] = node
        return node

    def add_edge(self, a: str, b: str):
        if a in self.nodes and b in self.nodes:
            self.edges.append((a, b))
            if b not in self.nodes[a].connections:
                self.nodes[a].connections.append(b)
            if a not in self.nodes[b].connections:
                self.nodes[b].connections.append(a)

    def _embed_graph(self):
        names = list(self.nodes.keys())
        adjacency = {n: set() for n in names}
        for a, b in self.edges:
            adjacency[a].add(b)
            adjacency[b].add(a)

        for i, name in enumerate(names):
            angle = 2 * math.pi * i / len(names)
            self.nodes[name].coords = [
                math.cos(angle) * (1 + len(adjacency[name]) * 0.2),
                math.sin(angle) * (1 + len(adjacency[name]) * 0.2),
            ]
            for d in range(2, self.target_dim):
                phase = d * math.pi / self.target_dim
                self.nodes[name].coords.append(
                    math.sin(angle + phase) * (1 + len(adjacency[name]) * 0.1)
                )

    def _cluster(self, threshold: float = 2.0) -> int:
        visited = set()
        cluster_id = 0
        names = list(self.nodes.keys())
        for name in names:
            if name in visited:
                continue
            stack = [name]
            while stack:
                n = stack.pop()
                if n in visited:
                    continue
                visited.add(n)
                self.nodes[n].cluster = cluster_id
                for other in names:
                    if other not in visited and other != n:
                        if self.nodes[n].distance_to(self.nodes[other]) < threshold:
                            stack.append(other)
            cluster_id += 1
        return cluster_id

    def fold(self) -> FoldResult:
        self._embed_graph()
        num_clusters = self._cluster()

        direct_edges = set()
        for a, b in self.edges:
            direct_edges.add((min(a, b), max(a, b)))

        shortcuts = []
        names = list(self.nodes.keys())
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if (min(a, b), max(a, b)) in direct_edges:
                    continue
                dist = self.nodes[a].distance_to(self.nodes[b])
                if dist < 1.5:
                    shortcuts.append((a, b, dist))

        shortcuts.sort(key=lambda x: x[2])

        original_dists = []
        for a, b in self.edges:
            node_a = DimensionalNode(name=a, coords=[0, 0])
            node_b = DimensionalNode(name=b, coords=[0, 0])
            original_dists.append(1.0)

        folded_dists = [self.nodes[a].distance_to(self.nodes[b]) for a, b in self.edges]
        avg_reduction = (sum(original_dists) - sum(folded_dists)) / max(sum(original_dists), 1)

        return FoldResult(
            original_edges=len(self.edges),
            folded_edges=len(self.edges),
            hidden_shortcuts=shortcuts[:10],
            cluster_count=num_clusters,
            avg_distance_reduction=avg_reduction,
        )

    def state(self) -> Dict:
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "dimension": self.target_dim,
            "clusters": len(set(n.cluster for n in self.nodes.values())),
            "node_details": {
                name: {"coords": [round(c, 3) for c in n.coords], "cluster": n.cluster}
                for name, n in self.nodes.items()
            },
        }


def demo():
    folder = DimensionalFolder(target_dim=3)
    print("=== Dimensional Fold Engine ===")

    nodes = ["nucleus", "agent_a", "agent_b", "sandbox", "protocol",
             "hex_vm", "pipeline", "observer", "meme_engine", "crystal"]
    for n in nodes:
        folder.add_node(n)

    edges = [
        ("nucleus", "agent_a"), ("nucleus", "agent_b"), ("nucleus", "sandbox"),
        ("agent_a", "protocol"), ("agent_b", "protocol"), ("sandbox", "hex_vm"),
        ("hex_vm", "pipeline"), ("pipeline", "observer"), ("observer", "meme_engine"),
        ("meme_engine", "crystal"), ("crystal", "nucleus"), ("agent_a", "sandbox"),
    ]
    for a, b in edges:
        folder.add_edge(a, b)

    result = folder.fold()
    print(f"  Original edges: {result.original_edges}")
    print(f"  Hidden shortcuts found: {len(result.hidden_shortcuts)}")
    for a, b, dist in result.hidden_shortcuts[:5]:
        print(f"    {a} <-> {b}: distance={dist:.3f}")
    print(f"  Clusters: {result.cluster_count}")
    print(f"  Avg distance reduction: {result.avg_distance_reduction:.3f}")

    state = folder.state()
    print("\nNode positions (3D):")
    for name, detail in list(state["node_details"].items())[:5]:
        print(f"  {name}: coords={detail['coords']}, cluster={detail['cluster']}")

    return state


if __name__ == "__main__":
    demo()
