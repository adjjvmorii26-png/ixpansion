from __future__ import annotations
"""Sacred Geometry — generates visual patterns from code structure.

Like ancient architects who built temples using sacred geometric
proportions, this module generates geometric patterns based on code
metrics. Complexity becomes radius, dependencies become angles,
and the resulting patterns reveal hidden symmetries in the codebase.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class GeometricPoint:
    x: float
    y: float
    label: str = ""
    radius: float = 1.0
    angle: float = 0.0

@dataclass
class SacredPattern:
    name: str
    points: List[GeometricPoint]
    symmetry_order: int
    golden_ratio_score: float
    total_area: float
    perimeter: float

class SacredGeometryEngine:
    PHI = (1 + math.sqrt(5)) / 2  # Golden ratio

    def __init__(self):
        self.patterns: Dict[str, SacredPattern] = {}
        self.modules: Dict[str, Dict] = {}

    def register_module(self, name: str, metrics: Dict):
        self.modules[name] = metrics

    def _fibonacci_spiral(self, n: int, scale: float = 1.0) -> List[GeometricPoint]:
        points = []
        for i in range(n):
            angle = i * self.PHI * 2 * math.pi
            radius = math.sqrt(i + 1) * scale
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            points.append(GeometricPoint(x=x, y=y, label=f"fib_{i}",
                                        radius=radius, angle=angle))
        return points

    def _metatrons_cube(self, center_x: float, center_y: float,
                        radius: float, n_circles: int = 13) -> List[GeometricPoint]:
        points = [GeometricPoint(center_x, center_y, "center", radius)]
        for i in range(n_circles - 1):
            angle = 2 * math.pi * i / (n_circles - 1)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append(GeometricPoint(x, y, f"circle_{i}", radius * 0.3, angle))
        return points

    def _flower_of_life(self, center_x: float, center_y: float,
                        radius: float, rings: int = 2) -> List[GeometricPoint]:
        points = [GeometricPoint(center_x, center_y, "seed", radius)]
        for ring in range(1, rings + 1):
            count = 6 * ring
            for i in range(count):
                angle = 2 * math.pi * i / count + (ring % 2) * math.pi / count
                r = radius * ring
                x = center_x + r * math.cos(angle)
                y = center_y + r * math.sin(angle)
                points.append(GeometricPoint(x, y, f"ring{ring}_{i}", radius * 0.5, angle))
        return points

    def generate_pattern(self, module_name: str) -> SacredPattern:
        if module_name not in self.modules:
            return SacredPattern(module_name, [], 1, 0.0, 0.0, 0.0)
        metrics = self.modules[module_name]
        complexity = metrics.get("complexity", 5)
        dependencies = metrics.get("dependencies", 3)
        size = metrics.get("size", 100)

        n_points = max(6, int(complexity * 2))
        symmetry = max(3, int(dependencies + 3))

        points = []
        for i in range(n_points):
            angle = 2 * math.pi * i / symmetry
            r = math.sqrt(size) * (1 + 0.1 * math.sin(i * self.PHI))
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            points.append(GeometricPoint(x, y, f"v_{i}", r, angle))

        area = 0.0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            area += points[i].x * points[j].y
            area -= points[j].x * points[i].y
        area = abs(area) / 2

        perimeter = 0.0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            dx = points[j].x - points[i].x
            dy = points[j].y - points[i].y
            perimeter += math.sqrt(dx * dx + dy * dy)

        golden_score = 0.0
        if perimeter > 0:
            compactness = 4 * math.pi * area / (perimeter * perimeter)
            golden_score = 1.0 - abs(compactness - 1.0 / self.PHI)

        pattern = SacredPattern(
            name=module_name, points=points,
            symmetry_order=symmetry,
            golden_ratio_score=round(golden_score, 4),
            total_area=round(area, 2),
            perimeter=round(perimeter, 2),
        )
        self.patterns[module_name] = pattern
        return pattern

    def generate_spiral(self, n: int = 20, scale: float = 1.0) -> List[GeometricPoint]:
        return self._fibonacci_spiral(n, scale)

    def generate_metatron(self, radius: float = 10.0) -> List[GeometricPoint]:
        return self._metatrons_cube(0, 0, radius)

    def generate_flower(self, radius: float = 5.0, rings: int = 2) -> List[GeometricPoint]:
        return self._flower_of_life(0, 0, radius, rings)

    def sacred_report(self) -> Dict:
        return {
            "modules": len(self.modules),
            "patterns": len(self.patterns),
            "avg_golden_score": sum(p.golden_ratio_score for p in self.patterns.values()) / max(len(self.patterns), 1),
            "patterns_detail": [
                {"name": p.name, "symmetry": p.symmetry_order,
                 "golden": p.golden_ratio_score, "area": p.total_area}
                for p in self.patterns.values()
            ],
        }


def demo():
    engine = SacredGeometryEngine()
    print("=== Sacred Geometry Engine ===")

    modules = {
        "nucleus": {"complexity": 8, "dependencies": 5, "size": 200},
        "agent": {"complexity": 4, "dependencies": 3, "size": 80},
        "sandbox": {"complexity": 6, "dependencies": 4, "size": 150},
        "protocol": {"complexity": 5, "dependencies": 2, "size": 100},
        "pipeline": {"complexity": 7, "dependencies": 6, "size": 180},
    }
    for name, metrics in modules.items():
        engine.register_module(name, metrics)
        pattern = engine.generate_pattern(name)
        print(f"  {name}: symmetry={pattern.symmetry_order}, "
              f"golden={pattern.golden_ratio_score}, area={pattern.total_area}")

    spiral = engine.generate_spiral(n=15, scale=1.0)
    print(f"\nFibonacci spiral: {len(spiral)} points")

    metatron = engine.generate_metatron(radius=10.0)
    print(f"Metatron's cube: {len(metatron)} circles")

    flower = engine.generate_flower(radius=3.0, rings=2)
    print(f"Flower of life: {len(flower)} petals")

    report = engine.sacred_report()
    print(f"\nAvg golden ratio score: {report['avg_golden_score']:.4f}")

    return report


if __name__ == "__main__":
    demo()
