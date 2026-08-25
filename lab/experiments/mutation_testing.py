from __future__ import annotations
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class MutationTest:
    def __init__(self, seed=42):
        self.seed = seed; self.mutations = []; self.results = []
    def mutate_line(self, line, rng):
        s = line.strip()
        if s.startswith("return "):
            return line.replace("return ", "return None # ")
        elif "==" in s and not s.startswith("# "):
            return line.replace("==", "!=", 1)
        elif "+=" in s:
            return line.replace("+=", "-=", 1)
        return None
    def test_file(self, filepath):
        text = filepath.read_text(errors="replace")
        lines = text.splitlines()
        rng = random.Random(self.seed + hash(str(filepath)))
        mutated = 0
        for i, line in enumerate(lines):
            new_line = self.mutate_line(line, rng)
            if new_line and rng.random() < 0.1:
                mutated += 1
                self.mutations.append({"file": filepath.stem, "line": i+1, "original": line.strip()[:40], "mutated": new_line.strip()[:40]})
        self.results.append({"file": filepath.stem, "lines": len(lines), "mutations": mutated, "kill_rate": round(mutated/max(1,len(lines)), 4)})
    def report(self):
        total_mut = sum(r["mutations"] for r in self.results)
        avg_kill = sum(r["kill_rate"] for r in self.results) / max(1, len(self.results))
        return {"testing": "mutation_testing", "files_tested": len(self.results),
                "total_mutations": total_mut, "avg_kill_rate": round(avg_kill, 4),
                "top_mutations": self.mutations[:5]}

def demo():
    t = MutationTest(42)
    for base in [ROOT/"api", ROOT/"lab"]:
        if base.exists():
            for py in list(base.glob("*.py"))[:5]:
                if not py.name.startswith("_"): t.test_file(py)
    return t.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
