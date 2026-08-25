from __future__ import annotations
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class PropagationField:
    def __init__(self, seed=42):
        self.seed = seed; self.sources = []
    def add_source(self, x, y, strength, frequency=1.0):
        self.sources.append({"x": x, "y": y, "strength": strength, "freq": frequency})
    def sample(self, x, y):
        total = 0.0
        for s in self.sources:
            dx, dy = x - s["x"], y - s["y"]
            dist = math.sqrt(dx*dx + dy*dy) + 0.01
            total += s["strength"] / (dist * dist) * math.sin(s["freq"] * dist)
        return round(total, 6)
    def heatmap(self, grid_size=10):
        heatmap = []
        for y in range(grid_size):
            row = []
            for x in range(grid_size):
                row.append(self.sample(x * 0.5, y * 0.5))
            heatmap.append(row)
        return heatmap
    def report(self):
        hm = self.heatmap(8)
        max_val = max(max(row) for row in hm)
        min_val = min(min(row) for row in hm)
        return {"field": "propagation_field", "sources": len(self.sources),
                "max_intensity": round(max_val, 4), "min_intensity": round(min_val, 4),
                "dynamic_range": round(max_val - min_val, 4)}

def demo():
    f = PropagationField(42)
    for i in range(5): f.add_source(i*2, i*2, 1.0 - i*0.15, frequency=1.0 + i*0.5)
    return f.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
