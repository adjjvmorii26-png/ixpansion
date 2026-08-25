"""Mutation Network — Graph of all possible module mutations and their effects.

Models the module evolution space as a directed graph where nodes are
module states and edges are mutations. Computes reachability, shortest
mutation paths, and identifies evolution dead-ends.
"""
from __future__ import annotations
import hashlib
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class MutationNode:
    """A state in the mutation network."""

    def __init__(self, name: str, subsystem: str, size: int, complexity: float):
        self.name = name
        self.subsystem = subsystem
        self.size = size
        self.complexity = complexity
        self.edges_out = []
        self.edges_in = []
        self.visited = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "subsystem": self.subsystem,
            "size": self.size,
            "complexity": round(self.complexity, 4),
            "out_degree": len(self.edges_out),
            "in_degree": len(self.edges_in),
        }


class MutationEdge:
    """A mutation transition between module states."""

    def __init__(self, source: str, target: str, mutation_type: str, cost: float):
        self.source = source
        self.target = target
        self.mutation_type = mutation_type
        self.cost = cost

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.mutation_type,
            "cost": round(self.cost, 4),
        }


class MutationNetwork:
    """Directed graph of module mutations."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.nodes: dict[str, MutationNode] = {}
        self.edges: list[MutationEdge] = []
        self.mutation_types = [
            "rename", "refactor", "split", "merge",
            "add_feature", "remove_feature", "optimize", "restructure",
        ]

    def add_node(self, name: str, subsystem: str, size: int) -> MutationNode:
        node = MutationNode(name, subsystem, size, size / 1000.0)
        self.nodes[name] = node
        return node

    def add_edge(self, source: str, target: str, mutation_type: str = "refactor") -> MutationEdge:
        if source not in self.nodes or target not in self.nodes:
            return None
        cost = abs(self.nodes[source].size - self.nodes[target].size) / 1000.0 + 0.1
        edge = MutationEdge(source, target, mutation_type, cost)
        self.edges.append(edge)
        self.nodes[source].edges_out.append(edge)
        self.nodes[target].edges_in.append(edge)
        return edge

    def compute_auto_edges(self):
        """Automatically create edges between related modules."""
        node_list = list(self.nodes.values())
        for i, a in enumerate(node_list):
            for b in node_list[i+1:]:
                # Same subsystem = more likely to mutate
                if a.subsystem == b.subsystem:
                    if abs(a.size - b.size) < 500:
                        self.add_edge(a.name, b.name, "refactor")
                    else:
                        self.add_edge(a.name, b.name, "split")
                # Similar size across subsystems = potential merge
                elif abs(a.size - b.size) < 200:
                    self.add_edge(a.name, b.name, "merge")

    def bfs_reachable(self, start: str, max_depth: int = 3) -> dict:
        """BFS from start node to find reachable mutations."""
        if start not in self.nodes:
            return {"error": f"node '{start}' not found"}

        from collections import deque
        queue = deque([(start, 0)])
        visited = {start: 0}
        reachable = []

        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for edge in self.nodes[current].edges_out:
                if edge.target not in visited:
                    visited[edge.target] = depth + 1
                    reachable.append({
                        "target": edge.target,
                        "depth": depth + 1,
                        "mutation": edge.mutation_type,
                        "cost": edge.cost,
                    })
                    queue.append((edge.target, depth + 1))

        return {
            "start": start,
            "reachable_count": len(reachable),
            "reachable": reachable,
            "max_depth": max_depth,
        }

    def find_dead_ends(self) -> list[dict]:
        """Find nodes with no outgoing edges (evolution dead-ends)."""
        dead_ends = []
        for name, node in self.nodes.items():
            if len(node.edges_out) == 0:
                dead_ends.append({
                    "name": name,
                    "subsystem": node.subsystem,
                    "size": node.size,
                    "reason": "no outgoing mutations — evolution stopped",
                })
        return dead_ends

    def find_hub_nodes(self, top_n: int = 5) -> list[dict]:
        """Find the most connected nodes (mutation hubs)."""
        scored = []
        for name, node in self.nodes.items():
            degree = len(node.edges_out) + len(node.edges_in)
            scored.append({"name": name, "degree": degree, "subsystem": node.subsystem})
        scored.sort(key=lambda x: x["degree"], reverse=True)
        return scored[:top_n]

    def report(self) -> dict:
        """Generate full mutation network report."""
        self.compute_auto_edges()
        dead_ends = self.find_dead_ends()
        hubs = self.find_hub_nodes()

        # Compute network metrics
        n = len(self.nodes)
        e = len(self.edges)
        avg_degree = (2 * e / n) if n > 0 else 0

        # Subsystem clustering
        clusters = {}
        for node in self.nodes.values():
            if node.subsystem not in clusters:
                clusters[node.subsystem] = []
            clusters[node.subsystem].append(node.name)

        return {
            "network": "mutation_network",
            "node_count": n,
            "edge_count": e,
            "avg_degree": round(avg_degree, 2),
            "dead_ends": dead_ends,
            "dead_end_count": len(dead_ends),
            "hubs": hubs,
            "clusters": {k: len(v) for k, v in clusters.items()},
            "mutation_types": self.mutation_types,
        }


def demo():
    net = MutationNetwork(seed=42)

    # Register modules from the codebase
    subsystems = {
        "lab": ROOT / "lab" / "experiments",
        "bridges": ROOT / "bridges",
        "api": ROOT / "api",
    }

    for subsys, base in subsystems.items():
        if not base.exists():
            continue
        for py in sorted(base.glob("*.py")):
            if py.name.startswith("_") or py.name.startswith("test_"):
                continue
            net.add_node(py.stem, subsys, py.stat().st_size)

    return net.report()


def main():
    import json
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
