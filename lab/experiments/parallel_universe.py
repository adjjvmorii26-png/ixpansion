from __future__ import annotations
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class Universe:
    def __init__(self, universe_id, seed):
        self.id = universe_id; self.rng = random.Random(seed)
        self.state = {"entropy": self.rng.random(), "complexity": self.rng.random(),
                      "cohesion": self.rng.random(), "innovation": self.rng.random()}
        self.history = [dict(self.state)]
    def tick(self):
        for k in self.state:
            self.state[k] = max(0, min(1, self.state[k] + self.rng.uniform(-0.05, 0.05)))
        self.history.append(dict(self.state))
    def divergence_from(self, other):
        return sum(abs(self.state[k] - other.state[k]) for k in self.state) / len(self.state)

class ParallelUniverseSimulator:
    def __init__(self, universe_count=5, seed=42):
        self.seed = seed
        self.universes = [Universe(i, seed + i * 1000) for i in range(universe_count)]
    def simulate(self, ticks=20):
        for _ in range(ticks):
            for u in self.universes: u.tick()
        divergences = []
        for i in range(len(self.universes)):
            for j in range(i+1, len(self.universes)):
                d = self.universes[i].divergence_from(self.universes[j])
                divergences.append({"pair": (i, j), "divergence": round(d, 4)})
        divergences.sort(key=lambda x: x["divergence"], reverse=True)
        return {"universes": len(self.universes), "ticks": ticks,
                "top_divergence": divergences[0] if divergences else None,
                "avg_divergence": round(sum(d["divergence"] for d in divergences)/max(1,len(divergences)), 4)}

def demo():
    sim = ParallelUniverseSimulator(5, 42)
    return {"parallel_universe": "parallel_universe_simulator", "simulation": sim.simulate(20)}
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
