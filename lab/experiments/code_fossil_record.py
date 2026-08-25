from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class CodeFossil:
    def __init__(self, name, pattern, age_estimate, rarity):
        self.name = name; self.pattern = pattern
        self.age_estimate = age_estimate; self.rarity = rarity

class CodeFossilRecord:
    def __init__(self, seed=42):
        self.seed = seed; self.fossils = []
    def excavate(self, filepath):
        text = filepath.read_text(errors="replace")
        lines = text.splitlines()
        patterns = []
        for i, l in enumerate(lines):
            s = l.strip()
            if s.startswith("class ") and "(object)" in s:
                patterns.append({"type": "old_style_class", "line": i+1, "snippet": s[:60]})
            elif "== None" in s or "!= None" in s:
                patterns.append({"type": "none_comparison", "line": i+1, "snippet": s[:60]})
            elif "except:" in s:
                patterns.append({"type": "bare_except", "line": i+1, "snippet": s[:60]})
            elif "global " in s and "=" in s:
                patterns.append({"type": "global_mutation", "line": i+1, "snippet": s[:60]})
        for p in patterns:
            rarity = "common" if p["type"] == "bare_except" else "uncommon" if p["type"] == "none_comparison" else "rare"
            self.fossils.append(CodeFossil(filepath.stem, p, len(lines), rarity))
    def report(self):
        by_type = {}; by_rarity = {}
        for f in self.fossils:
            by_type[f.pattern["type"]] = by_type.get(f.pattern["type"], 0) + 1
            by_rarity[f.rarity] = by_rarity.get(f.rarity, 0) + 1
        return {"record": "code_fossil_record", "fossils_found": len(self.fossils),
                "by_type": by_type, "by_rarity": by_rarity,
                "samples": [{"name": f.name, "type": f.pattern["type"], "line": f.pattern["line"]} for f in self.fossils[:10]]}

def demo():
    r = CodeFossilRecord(42)
    for base in [ROOT/"api", ROOT/"lab", ROOT/"bridges"]:
        if base.exists():
            for py in base.rglob("*.py"):
                if not py.name.startswith("_") and not py.name.startswith("test_"):
                    r.excavate(py)
    return r.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
