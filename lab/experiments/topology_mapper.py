"""Topology Mapper — Maps the codebase as a topological space.

Computes Betti numbers, Euler characteristics, and connected components
to understand the "shape" of the code.
"""
from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class TopologyMapper:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.nodes: dict[str, dict] = {}
        self.edges: list[tuple[str, str]] = []

    def add_module(self, name: str, subsystem: str, functions: int, classes: int):
        self.nodes[name] = {"subsystem": subsystem, "functions": functions, "classes": classes}

    def add_edge(self, a: str, b: str):
        if a in self.nodes and b in self.nodes:
            self.edges.append((a, b))

    def auto_connect(self):
        """Connect modules in same subsystem."""
        by_sub = {}
        for name, data in self.nodes.items():
            by_sub.setdefault(data["subsystem"], []).append(name)
        for subsys, mods in by_sub.items():
            for i in range(len(mods) - 1):
                self.add_edge(mods[i], mods[i + 1])

    def compute_components(self) -> int:
        visited = set()
        components = 0
        adj = {}
        for a, b in self.edges:
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
        for node in self.nodes:
            if node not in visited:
                components += 1
                stack = [node]
                while stack:
                    n = stack.pop()
                    if n in visited:
                        continue
                    visited.add(n)
                    for neighbor in adj.get(n, []):
                        if neighbor not in visited:
                            stack.append(neighbor)
        return components

    def euler_characteristic(self) -> int:
        v = len(self.nodes)
        e = len(self.edges)
        # f = faces (approximated by cycles)
        f = max(0, e - v + self.compute_components())
        return v - e + f

    def betti_numbers(self) -> dict:
        components = self.compute_components()
        v = len(self.nodes)
        e = len(self.edges)
        b0 = components
        b1 = max(0, e - v + components)
        return {"b0": b0, "b1": b1, "b2": 0}

    def report(self) -> dict:
        self.auto_connect()
        components = self.compute_components()
        euler = self.euler_characteristic()
        betti = self.betti_numbers()
        return {
            "topology": "topology_mapper",
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "components": components,
            "euler_characteristic": euler,
            "betti_numbers": betti,
            "connected": components == 1,
            "shape": "connected" if components == 1 else f"disconnected ({components} components)",
        }


def demo():
    tm = TopologyMapper(seed=42)
    api_dir = ROOT / "api"
    if api_dir.exists():
        for py in api_dir.glob("*.py"):
            if py.name.startswith("_"):
                continue
            text = py.read_text(errors="replace")
            funcs = sum(1 for ln in text.splitlines() if ln.strip().startswith("def "))
            classes = sum(1 for ln in text.splitlines() if ln.strip().startswith("class "))
            tm.add_module(py.stem, "api", funcs, classes)
    lab_dir = ROOT / "lab" / "experiments"
    if lab_dir.exists():
        for py in lab_dir.glob("*.py"):
            if py.name.startswith("_"):
                continue
            text = py.read_text(errors="replace")
            funcs = sum(1 for ln in text.splitlines() if ln.strip().startswith("def "))
            classes = sum(1 for ln in text.splitlines() if ln.strip().startswith("class "))
            tm.add_module(py.stem, "lab", funcs, classes)
    return tm.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
