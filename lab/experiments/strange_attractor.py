from __future__ import annotations
"""Strange Attractor — maps system behavior to chaotic attractors.

System states are plotted in phase space. If the system exhibits chaotic
behavior, it forms strange attractors (like the Lorenz attractor). This
module detects and classifies the type of attractor, measuring its
fractal dimension and Lyapunov exponent.
"""
import math
import random
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class PhasePoint:
    x: float
    y: float
    z: float
    timestamp: int = 0

@dataclass
class AttractorProperties:
    name: str
    dimension: float
    lyapunov_exponent: float
    basin_size: int
    is_strange: bool
    embedding: List[Tuple[float, float, float]] = field(default_factory=list)

class StrangeAttractorMapper:
    def __init__(self, sigma: float = 10.0, rho: float = 28.0, beta: float = 8/3):
        self.sigma = sigma
        self.rho = rho
        self.beta = beta
        self.points: List[PhasePoint] = []
        self.tick = 0

    def lorenz_step(self, x: float, y: float, z: float, dt: float = 0.01) -> Tuple[float, float, float]:
        dx = self.sigma * (y - x) * dt
        dy = (x * (self.rho - z) - y) * dt
        dz = (x * y - self.beta * z) * dt
        return x + dx, y + dy, z + dz

    def rossler_step(self, x: float, y: float, z: float,
                     a: float = 0.2, b: float = 0.2, c: float = 5.7,
                     dt: float = 0.01) -> Tuple[float, float, float]:
        dx = (-y - z) * dt
        dy = (x + a * y) * dt
        dy = (x + a * y) * dt
        dz = (b + z * (x - c)) * dt
        return x + dx, y + dy, z + dz

    def generate(self, x0: float = 1.0, y0: float = 1.0, z0: float = 1.0,
                 steps: int = 500, system: str = "lorenz") -> List[PhasePoint]:
        x, y, z = x0, y0, z0
        for i in range(steps):
            if system == "lorenz":
                x, y, z = self.lorenz_step(x, y, z)
            else:
                x, y, z = self.rossler_step(x, y, z)
            self.points.append(PhasePoint(x=x, y=y, z=z, timestamp=i))
            self.tick += 1
        return self.points

    def _box_counting_dimension(self) -> float:
        if len(self.points) < 10:
            return 0.0
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        x_range = max(xs) - min(xs) + 1e-10
        y_range = max(ys) - min(ys) + 1e-10
        scales = [0.5, 0.25, 0.125, 0.0625]
        counts = []
        for scale in scales:
            boxes = set()
            for p in self.points:
                bx = int((p.x - min(xs)) / (x_range * scale))
                by = int((p.y - min(ys)) / (y_range * scale))
                boxes.add((bx, by))
            counts.append(len(boxes))
        if len(counts) < 2 or counts[-1] == 0:
            return 1.5
        log_scales = [math.log(1.0 / s) for s in scales]
        log_counts = [math.log(max(c, 1)) for c in counts]
        n = len(log_scales)
        mean_x = sum(log_scales) / n
        mean_y = sum(log_counts) / n
        num = sum((log_scales[i] - mean_x) * (log_counts[i] - mean_y) for i in range(n))
        den = sum((log_scales[i] - mean_x) ** 2 for i in range(n))
        return num / den if den > 0 else 1.5

    def _lyapunov_exponent(self) -> float:
        if len(self.points) < 20:
            return 0.0
        divergences = []
        for i in range(1, min(100, len(self.points))):
            dx = self.points[i].x - self.points[i-1].x
            dy = self.points[i].y - self.points[i-1].y
            dz = self.points[i].z - self.points[i-1].z
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist > 0:
                divergences.append(math.log(dist + 1e-10))
        if not divergences:
            return 0.0
        return sum(divergences) / len(divergences)

    def analyze(self, system: str = "lorenz") -> AttractorProperties:
        if not self.points:
            self.generate(system=system)
        dim = self._box_counting_dimension()
        lyap = self._lyapunov_exponent()
        is_strange = dim > 1.5 and lyap > 0
        return AttractorProperties(
            name=f"{system}_attractor",
            dimension=round(dim, 4),
            lyapunov_exponent=round(lyap, 6),
            basin_size=len(self.points),
            is_strange=is_strange,
            embedding=[(p.x, p.y, p.z) for p in self.points[:50]],
        )

    def state(self) -> Dict:
        if not self.points:
            return {"points": 0}
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        zs = [p.z for p in self.points]
        return {
            "points": len(self.points),
            "x_range": (round(min(xs), 2), round(max(xs), 2)),
            "y_range": (round(min(ys), 2), round(max(ys), 2)),
            "z_range": (round(min(zs), 2), round(max(zs), 2)),
        }


def demo():
    mapper = StrangeAttractorMapper()
    print("=== Strange Attractor Mapper ===")

    mapper.generate(x0=1.0, y0=1.0, z0=1.0, steps=500, system="lorenz")
    lorenz = mapper.analyze("lorenz")
    print(f"\nLorenz attractor:")
    print(f"  Dimension: {lorenz.dimension}")
    print(f"  Lyapunov: {lorenz.lyapunov_exponent}")
    print(f"  Strange: {lorenz.is_strange}")
    print(f"  Points: {lorenz.basin_size}")

    mapper2 = StrangeAttractorMapper()
    mapper2.generate(x0=1.0, y0=1.0, z0=1.0, steps=500, system="rossler")
    rossler = mapper2.analyze("rossler")
    print(f"\nRössler attractor:")
    print(f"  Dimension: {rossler.dimension}")
    print(f"  Lyapunov: {rossler.lyapunov_exponent}")
    print(f"  Strange: {rossler.is_strange}")

    state = mapper.state()
    print(f"\nLorenz state: {state}")

    return {"lorenz": {"dim": lorenz.dimension, "lyap": lorenz.lyapunov_exponent},
            "rossler": {"dim": rossler.dimension, "lyap": rossler.lyapunov_exponent}}


if __name__ == "__main__":
    demo()
