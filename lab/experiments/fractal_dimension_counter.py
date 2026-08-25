from __future__ import annotations
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class FractalDimensionCounter:
    def __init__(self, seed=42):
        self.seed = seed; self.datasets = {}
    def count_box(self, points, box_size):
        boxes = set()
        for x, y in points:
            boxes.add((int(x // box_size), int(y // box_size)))
        return len(boxes)
    def box_count_dimension(self, points, sizes=None):
        if sizes is None: sizes = [0.5, 1.0, 2.0, 4.0, 8.0]
        counts = []
        for s in sizes:
            counts.append((math.log(1.0/s) if s > 0 else 0, math.log(max(1, self.count_box(points, s)))))
        if len(counts) < 2: return 0.0
        n = len(counts)
        sum_x = sum(c[0] for c in counts)
        sum_y = sum(c[1] for c in counts)
        sum_xy = sum(c[0]*c[1] for c in counts)
        sum_xx = sum(c[0]**2 for c in counts)
        denom = n * sum_xx - sum_x**2
        if denom == 0: return 0.0
        return round((n * sum_xy - sum_x * sum_y) / denom, 4)
    def report(self):
        rng = __import__("random").Random(self.seed)
        points = [(rng.gauss(5, 2), rng.gauss(5, 2)) for _ in range(100)]
        dim = self.box_count_dimension(points)
        return {"counter": "fractal_dimension_counter", "dimension": dim,
                "point_count": len(points),
                "classification": "fractal" if 1.0 < dim < 2.0 else "euclidean" if dim <= 1.0 else "space_filling"}

def demo():
    c = FractalDimensionCounter(42); return c.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
