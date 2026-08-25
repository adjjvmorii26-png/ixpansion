from __future__ import annotations
import random

class SignalPropagator:
    def __init__(self, seed=42):
        self.seed=seed; self.nodes={}; self.edges=[]; self.logs=[]
    def add_node(self, name, latency=0.1, bandwidth=1.0):
        self.nodes[name]={"latency":latency,"bandwidth":bandwidth,"signal":0.0}
    def add_edge(self, a, b, loss=0.1):
        if a in self.nodes and b in self.nodes: self.edges.append((a,b,loss))
    def propagate(self, source, signal=1.0, max_hops=5):
        if source not in self.nodes: return {"error":"not found"}
        reached={source:signal}; frontier=[(source,signal,0)]
        while frontier:
            node,st,hops = frontier.pop(0)
            if hops>=max_hops: continue
            self.nodes[node]["signal"]=max(self.nodes[node]["signal"],st)
            for a,b,loss in self.edges:
                nb = b if a==node else (a if b==node else None)
                if nb and nb not in reached:
                    ns = st*(1-loss)*self.nodes[nb]["bandwidth"]
                    if ns>0.01: reached[nb]=ns; frontier.append((nb,ns,hops+1))
        self.logs.append({"source":source,"reached":len(reached)})
        return {"source":source,"reached":len(reached)}
    def report(self):
        active={n:round(d["signal"],4) for n,d in self.nodes.items() if d["signal"]>0}
        return {"propagator":"signal_propagation","nodes":len(self.nodes),
                "edges":len(self.edges),"active":active}

def demo():
    p = SignalPropagator(42)
    import pathlib; ROOT=pathlib.Path(__file__).resolve().parents[2]
    api=ROOT/"api"
    if api.exists():
        for py in api.glob("*.py"):
            if not py.name.startswith("_"): p.add_node(py.stem,random.Random(hash(py.stem)).uniform(0.05,0.3))
    ns=list(p.nodes.keys())
    for i in range(len(ns)-1): p.add_edge(ns[i],ns[i+1],random.Random(i).uniform(0.05,0.2))
    if ns: p.propagate(ns[0],1.0,4)
    return p.report()
def main():
    import json; print(json.dumps(demo(),indent=2))
if __name__=="__main__": main()
