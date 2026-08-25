from __future__ import annotations
import random
from collections import Counter

class EmergenceDetector:
    def __init__(self, seed=42):
        self.seed=seed; self.behaviors=[]; self.emergences=[]
    def record(self, agent, btype):
        self.behaviors.append({"agent":agent,"type":btype})
    def detect(self):
        tc = Counter(b["type"] for b in self.behaviors)
        ab = {}
        for b in self.behaviors:
            ab.setdefault(b["agent"],[]).append(b["type"])
        for t,c in tc.items():
            if c>2:
                au = sum(1 for v in ab.values() if t in v)
                if au>1:
                    self.emergences.append({"pattern":t,"count":c,"agents":au,
                                           "score":round(c*au/max(1,len(self.behaviors)),4)})
        self.emergences.sort(key=lambda e:e["score"],reverse=True)
        return self.emergences
    def report(self):
        self.detect()
        return {"detector":"emergence_detector","behaviors":len(self.behaviors),
                "emergences":len(self.emergences),"top":self.emergences[:5]}

def demo():
    d = EmergenceDetector(42); rng=random.Random(42)
    agents=["scout_0","scout_1","sentinel_0","architect_0"]
    for _ in range(30):
        d.record(rng.choice(agents),rng.choice(["move","scan","build","alert","rest"]))
    return d.report()
def main():
    import json; print(json.dumps(demo(),indent=2))
if __name__=="__main__": main()
