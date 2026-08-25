from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class TemporalLoopDetector:
    def __init__(self, seed=42):
        self.seed = seed; self.nodes = {}; self.edges = []; self.loops = []
    def add_module(self, name, imports):
        self.nodes[name] = imports
    def detect_loops(self):
        self.loops = []
        visited = set(); path = []
        def dfs(name):
            if name in path:
                loop_start = path.index(name)
                self.loops.append(path[loop_start:] + [name])
                return
            if name in visited: return
            visited.add(name); path.append(name)
            for imp in self.nodes.get(name, []):
                if imp in self.nodes: dfs(imp)
            path.pop()
        for name in self.nodes: dfs(name)
        return self.loops
    def report(self):
        self.detect_loops()
        return {"detector": "temporal_loop_detector", "modules": len(self.nodes),
                "loops_found": len(self.loops), "loop_details": [l[:4] for l in self.loops[:5]]}

def demo():
    d = TemporalLoopDetector(42)
    for base in [ROOT/"api", ROOT/"lab"]:
        if base.exists():
            for py in list(base.glob("*.py"))[:10]:
                if not py.name.startswith("_"):
                    text = py.read_text(errors="replace")
                    imports = [l.strip().split(".")[0].replace("from ","").replace("import ","")
                              for l in text.splitlines() if l.strip().startswith(("from ","import "))]
                    d.add_module(py.stem, imports)
    return d.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
