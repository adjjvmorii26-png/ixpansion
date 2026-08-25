from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class CausalLoopDetector:
    def __init__(self, seed=42):
        self.seed = seed; self.nodes = {}; self.edges = []; self.loops = []
    def add_node(self, name, module, causality_score=0.5):
        self.nodes[name] = {"module": module, "score": causality_score}
    def add_edge(self, a, b):
        if a in self.nodes and b in self.nodes: self.edges.append((a, b))
    def find_loops(self):
        self.loops = []
        adj = {}
        for a, b in self.edges:
            adj.setdefault(a, []).append(b)
        def dfs(node, path, visited):
            for neighbor in adj.get(node, []):
                if neighbor in path:
                    loop = path[path.index(neighbor):] + [neighbor]
                    self.loops.append(loop)
                elif neighbor not in visited:
                    visited.add(neighbor)
                    dfs(neighbor, path + [neighbor], visited)
        for node in self.nodes:
            dfs(node, [node], {node})
        return self.loops
    def report(self):
        self.find_loops()
        return {"detector": "causal_loop_detector", "nodes": len(self.nodes),
                "edges": len(self.edges), "loops": len(self.loops),
                "loop_details": [l[:5] for l in self.loops[:5]]}

def demo():
    d = CausalLoopDetector(42)
    import pathlib; ROOT = pathlib.Path(__file__).resolve().parents[2]
    for base_name, base_path in [("api", ROOT/"api"), ("lab", ROOT/"lab")]:
        if base_path.exists():
            for py in base_path.glob("*.py"):
                if not py.name.startswith("_") and not py.name.startswith("test_"):
                    d.add_node(py.stem, base_name, 0.5)
    ns = list(d.nodes.keys())
    for i in range(len(ns)-1): d.add_edge(ns[i], ns[i+1])
    for i in range(0, len(ns)-2, 3): d.add_edge(ns[i+2], ns[i])
    return d.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
