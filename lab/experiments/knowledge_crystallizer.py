from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class KnowledgeCrystallizer:
    def __init__(self, seed=42):
        self.seed = seed; self.crystals = []
    def crystallize(self, filepath):
        text = filepath.read_text(errors="replace"); lines = text.splitlines()
        funcs = [l.strip().split("(")[0].replace("def ","") for l in lines if l.strip().startswith("def ")]
        classes = [l.strip().split("class ")[1].split("(")[0] for l in lines if l.strip().startswith("class ")]
        imports = [l.strip() for l in lines if l.strip().startswith(("import ","from "))]
        crystal = {"module":filepath.stem,"functions":funcs,"classes":classes,
                   "import_count":len(imports),"lines":len(lines),
                   "hash":hashlib.md5(str(funcs).encode()).hexdigest()[:8]}
        self.crystals.append(crystal); return crystal
    def analyze(self):
        all_funcs=[f for c in self.crystals for f in c["functions"]]
        prefixes={}
        for f in all_funcs:
            p=f.split("_")[0]; prefixes[p]=prefixes.get(p,0)+1
        return {"total":len(self.crystals),"functions":len(all_funcs),
                "top_prefixes":dict(sorted(prefixes.items(),key=lambda x:x[1],reverse=True)[:10])}
    def report(self):
        return {"crystallizer":"knowledge_crystallizer","patterns":self.analyze(),"crystals":self.crystals[:10]}

def demo():
    c = KnowledgeCrystallizer(42)
    for base in [ROOT/"api",ROOT/"lab"/"experiments"]:
        if base.exists():
            for py in base.glob("*.py"):
                if not py.name.startswith("_"): c.crystallize(py)
    return c.report()
def main():
    import json; print(json.dumps(demo(),indent=2))
if __name__=="__main__": main()
