from __future__ import annotations
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class Genome:
    def __init__(self, genes):
        self.genes=genes; self.fitness=sum(genes.values())/max(1,len(genes))
    def mutate(self, rate=0.1, seed=42):
        rng=random.Random(seed); m={}
        for g,v in self.genes.items():
            m[g]=max(0,min(1,v+rng.uniform(-0.2,0.2))) if rng.random()<rate else v
        return Genome(m)
    def crossover(self, other, seed=42):
        rng=random.Random(seed); c={}
        for g in self.genes: c[g]=self.genes[g] if rng.random()<0.5 else other.genes.get(g,self.genes[g])
        return Genome(c)
    def to_dict(self): return {"genes":{k:round(v,4) for k,v in self.genes.items()},"fitness":round(self.fitness,4)}

class GenomeSequencer:
    def __init__(self, seed=42):
        self.seed=seed; self.pops=[]; self.genes=["energy","cognition","social","adaptation","curiosity","resilience"]
    def initialize(self, size=20):
        rng=random.Random(self.seed)
        self.pops.append([Genome({g:rng.uniform(0.2,0.9) for g in self.genes}) for _ in range(size)])
    def evolve(self, gens=10):
        pop=list(self.pops[-1]) if self.pops else []
        for g in range(gens):
            pop.sort(key=lambda x:x.fitness,reverse=True)
            surv=pop[:len(pop)//2]; off=[]
            rng=random.Random(self.seed+g)
            while len(off)<len(pop):
                p1,p2=rng.choice(surv),rng.choice(surv)
                child=p1.crossover(p2,rng.randint(0,10000)).mutate(0.15,rng.randint(0,10000))
                off.append(child)
            pop=off
        self.pops.append(pop)
    def report(self):
        if not self.pops: return {"sequencer":"genome_sequencer","pops":0}
        last=self.pops[-1]; avg=sum(g.fitness for g in last)/max(1,len(last))
        best=max(last,key=lambda g:g.fitness)
        return {"sequencer":"genome_sequencer","generations":len(self.pops)-1,
                "population":len(last),"avg_fitness":round(avg,4),"best":best.to_dict()}

def demo():
    s=GenomeSequencer(42); s.initialize(20); s.evolve(10); return s.report()
def main():
    import json; print(json.dumps(demo(),indent=2))
if __name__=="__main__": main()
