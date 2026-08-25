from __future__ import annotations
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class SystemMetabolism:
    def __init__(self, seed=42):
        self.seed = seed; self.nutrients = {"energy": 100.0, "memory": 50.0, "bandwidth": 75.0}
        self.waste = {}; self.history = []
    def consume(self, nutrient, amount):
        if nutrient in self.nutrients:
            self.nutrients[nutrient] = max(0, self.nutrients[nutrient] - amount)
    def produce(self, nutrient, amount):
        self.nutrients[nutrient] = self.nutrients.get(nutrient, 0) + amount
    def metabolize(self):
        rng = random.Random(len(self.history))
        self.consume("energy", rng.uniform(0.5, 2.0))
        self.consume("memory", rng.uniform(0.2, 1.0))
        self.produce("energy", rng.uniform(0.1, 0.5))
        self.waste["entropy"] = self.waste.get("entropy", 0) + rng.uniform(0.1, 0.3)
        snapshot = {k: round(v, 2) for k, v in self.nutrients.items()}
        self.history.append(snapshot)
        return snapshot
    def health(self):
        total = sum(self.nutrients.values())
        return round(total / 300.0, 4)
    def report(self):
        return {"metabolism": "system_metabolism", "nutrients": {k: round(v, 2) for k, v in self.nutrients.items()},
                "waste": {k: round(v, 2) for k, v in self.waste.items()},
                "health": self.health(), "cycles": len(self.history)}

def demo():
    m = SystemMetabolism(42)
    for _ in range(10): m.metabolize()
    return m.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
