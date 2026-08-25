from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class CodebaseGenome:
    def __init__(self, seed=42):
        self.seed = seed; self.chromosomes = {}
    def sequence_chromosome(self, name, filepath):
        text = filepath.read_text(errors="replace")
        lines = text.splitlines()
        funcs = [l.strip().split("(")[0].replace("def ","") for l in lines if l.strip().startswith("def ")]
        classes = [l.strip().split("class ")[1].split("(")[0] for l in lines if l.strip().startswith("class ")]
        self.chromosomes[name] = {"functions": len(funcs), "classes": len(classes),
                                   "lines": len(lines), "size": filepath.stat().st_size,
                                   "hash": hashlib.md5(str(funcs).encode()).hexdigest()[:8]}
    def fitness(self):
        if not self.chromosomes: return 0.0
        total_lines = sum(c["lines"] for c in self.chromosomes.values())
        total_funcs = sum(c["functions"] for c in self.chromosomes.values())
        return round(total_funcs / max(1, total_lines / 100), 4)
    def report(self):
        return {"genome": "codebase_genome", "chromosomes": len(self.chromosomes),
                "fitness": self.fitness(),
                "details": {k: v for k, v in list(self.chromosomes.items())[:10]}}

def demo():
    g = CodebaseGenome(42)
    for py in (ROOT/"api").glob("*.py"):
        if not py.name.startswith("_"): g.sequence_chromosome(py.stem, py)
    return g.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
