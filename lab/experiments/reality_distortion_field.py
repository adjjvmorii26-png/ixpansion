from __future__ import annotations
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class DistortionField:
    def __init__(self, seed=42):
        self.seed = seed; self.sources = []; self.measurements = []
    def add_source(self, name, x, y, strength):
        self.sources.append({"name": name, "x": x, "y": y, "strength": strength})
    def measure(self, x, y):
        total_distortion = 0.0
        for s in self.sources:
            dx, dy = x - s["x"], y - s["y"]
            dist = math.sqrt(dx*dx + dy*dy) + 0.1
            distortion = s["strength"] / (dist * dist)
            total_distortion += distortion
        warped = x * (1 + total_distortion * 0.1), y * (1 + total_distortion * 0.1)
        self.measurements.append({"original": (x, y), "warped": (round(warped[0], 4), round(warped[1], 4)),
                                  "distortion": round(total_distortion, 4)})
        return warped
    def report(self):
        avg_dist = sum(m["distortion"] for m in self.measurements) / max(1, len(self.measurements))
        return {"field": "reality_distortion_field", "sources": len(self.sources),
                "measurements": len(self.measurements), "avg_distortion": round(avg_dist, 4)}

def demo():
    f = DistortionField(42)
    f.add_source("consciousness", 5, 5, 2.0)
    f.add_source("entropy", 2, 8, 1.5)
    f.add_source("innovation", 8, 3, 1.8)
    for i in range(10): f.measure(i * 0.5, i * 0.5)
    return f.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
