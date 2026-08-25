from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class EntanglementGraph:
    def __init__(self, seed=42):
        self.seed=seed; self.nodes={}; self.entanglements=[]
    def add_node(self, name, subsystem, size):
        self.nodes[name]={"subsystem":subsystem,"size":size}
    def compute(self, a, b):
        if a not in self.nodes or b not in self.nodes: return 0.0
        na,nb=self.nodes[a],self.nodes[b]
        sr=min(na["size"],nb["size"])/max(1,max(na["size"],nb["size"]))
        sm=1.0 if na["subsystem"]==nb["subsystem"] else 0.3
        return round(sr*sm,4)
    def build(self, threshold=0.3):
        self.entanglements=[]; ns=list(self.nodes.keys())
        for i,a in enumerate(ns):
            for b in ns[i+1:]:
                e=self.compute(a,b)
                if e>=threshold:
                    state="phi+" if e>0.7 else "psi+" if e>0.5 else "psi-"
                    self.entanglements.append({"pair":(a,b),"strength":e,"state":state})
    def report(self):
        self.build()
        avg=sum(e["strength"] for e in self.entanglements)/max(1,len(self.entanglements))
        states={}
        for e in self.entanglements: s=e["state"]; states[s]=states.get(s,0)+1
        return {"graph":"entanglement_graph","nodes":len(self.nodes),
                "entanglements":len(self.entanglements),"avg":round(avg,4),
                "states":states,"top":sorted(self.entanglements,key=lambda e:e["strength"],reverse=True)[:5]}

def demo():
    g=EntanglementGraph(42)
    for bn,bp in [("api",ROOT/"api"),("lab",ROOT/"lab"/"experiments")]:
        if bp.exists():
            for py in bp.glob("*.py"):
                if not py.name.startswith("_"): g.add_node(py.stem,bn,py.stat().st_size)
    return g.report()
def main():
    import json; print(json.dumps(demo(),indent=2))
if __name__=="__main__": main()
