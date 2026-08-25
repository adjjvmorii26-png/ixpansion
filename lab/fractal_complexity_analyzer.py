"""Fractal Complexity Analyzer — Measures code complexity using fractal dimension.

Applies fractal analysis to code structure, finding self-similar patterns
at different scales and measuring the fractal dimension of the codebase.
"""
from __future__ import annotations
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FractalComplexityAnalyzer:
    def __init__(self, seed=42):
        self.seed = seed
        self.measurements: list[dict] = []

    def analyze_file(self, filepath: Path) -> dict:
        text = filepath.read_text(errors="replace")
        lines = text.splitlines()
        indent_levels = []
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indent_levels.append(indent)
        if not indent_levels:
            return {"name": filepath.stem, "dimension": 0, "complexity": 0}
        max_indent = max(indent_levels)
        unique_indents = len(set(indent_levels))
        indent_entropy = 0.0
        from collections import Counter
        counts = Counter(indent_levels)
        for count in counts.values():
            p = count / len(indent_levels)
            if p > 0:
                indent_entropy -= p * math.log2(p)
        box_counts = []
        for box_size in [1, 2, 4, 8, 16]:
            boxes = len(set(i // box_size for i in indent_levels))
            box_counts.append((math.log(1.0/box_size) if box_size > 1 else 0, math.log(max(1, boxes))))
        if len(box_counts) >= 2:
            n = len(box_counts)
            sx = sum(b[0] for b in box_counts)
            sy = sum(b[1] for b in box_counts)
            sxy = sum(b[0]*b[1] for b in box_counts)
            sxx = sum(b[0]**2 for b in box_counts)
            denom = n * sxx - sx*sx
            dimension = (n * sxy - sx*sy) / denom if denom != 0 else 0
        else:
            dimension = 0
        measurement = {
            "name": filepath.stem, "lines": len(lines),
            "max_indent": max_indent, "unique_indents": unique_indents,
            "indent_entropy": round(indent_entropy, 4),
            "fractal_dimension": round(abs(dimension), 4),
            "complexity_score": round(indent_entropy * abs(dimension), 4),
        }
        self.measurements.append(measurement)
        return measurement

    def report(self) -> dict:
        if not self.measurements:
            return {"analyzer": "fractal_complexity_analyzer", "files": 0}
        avg_dim = sum(m["fractal_dimension"] for m in self.measurements) / len(self.measurements)
        avg_entropy = sum(m["indent_entropy"] for m in self.measurements) / len(self.measurements)
        return {
            "analyzer": "fractal_complexity_analyzer",
            "files": len(self.measurements),
            "avg_fractal_dimension": round(avg_dim, 4),
            "avg_indent_entropy": round(avg_entropy, 4),
            "most_complex": max(self.measurements, key=lambda m: m["complexity_score"]),
            "simplest": min(self.measurements, key=lambda m: m["complexity_score"]),
        }


def demo():
    analyzer = FractalComplexityAnalyzer(seed=42)
    for py in list((ROOT / "lab").glob("*.py"))[:10]:
        if not py.name.startswith("_"):
            analyzer.analyze_file(py)
    for py in list((ROOT / "api").glob("*.py"))[:5]:
        if not py.name.startswith("_"):
            analyzer.analyze_file(py)
    return analyzer.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
