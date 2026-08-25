from __future__ import annotations
"""Temporal Pattern Recognizer — finds recurring structures across time scales.

Like fractals that repeat at every scale, some patterns in the codebase
recur at different time scales: daily cycles, weekly rhythms, and
evolutionary epochs. This module detects those self-similar patterns.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class TemporalPattern:
    name: str
    period: int
    strength: float
    scale: str
    evidence: List[float]

class TemporalPatternRecognizer:
    def __init__(self, series: List[float] = None):
        self.series = series or []
        self.patterns: List[TemporalPattern] = []

    def set_series(self, data: List[float]):
        self.series = data

    def _autocorrelation(self, lag: int) -> float:
        if len(self.series) < lag + 2:
            return 0.0
        n = len(self.series) - lag
        mean = sum(self.series) / len(self.series)
        num = sum((self.series[i] - mean) * (self.series[i + lag] - mean) for i in range(n))
        den = sum((x - mean) ** 2 for x in self.series)
        return num / den if den > 0 else 0.0

    def detect(self, min_period: int = 2, max_period: int = None) -> List[TemporalPattern]:
        self.patterns.clear()
        if max_period is None:
            max_period = len(self.series) // 2
        for period in range(min_period, min(max_period + 1, len(self.series) // 2)):
            correlation = self._autocorrelation(period)
            if abs(correlation) > 0.3:
                if period <= 7:
                    scale = "daily"
                elif period <= 30:
                    scale = "weekly"
                else:
                    scale = "epoch"
                self.patterns.append(TemporalPattern(
                    name=f"pattern_p{period}",
                    period=period, strength=abs(correlation),
                    scale=scale,
                    evidence=[self.series[i] for i in range(0, len(self.series), period)],
                ))
        self.patterns.sort(key=lambda p: p.strength, reverse=True)
        return self.patterns

    def dominant_period(self) -> int:
        if not self.patterns:
            return 0
        return self.patterns[0].period

    def report(self) -> Dict:
        scale_counts = {}
        for p in self.patterns:
            scale_counts[p.scale] = scale_counts.get(p.scale, 0) + 1
        return {
            "series_length": len(self.series),
            "patterns_found": len(self.patterns),
            "dominant_period": self.dominant_period(),
            "scales": scale_counts,
            "top_patterns": [
                {"period": p.period, "strength": round(p.strength, 4), "scale": p.scale}
                for p in self.patterns[:5]
            ],
        }


def demo():
    import random
    rng = random.Random(42)
    series = [50 + 20 * math.sin(i * 2 * math.pi / 7) + rng.gauss(0, 5)
              for i in range(100)]
    recognizer = TemporalPatternRecognizer(series)
    print("=== Temporal Pattern Recognizer ===")
    patterns = recognizer.detect()
    report = recognizer.report()
    print(f"  Series length: {report['series_length']}")
    print(f"  Patterns found: {report['patterns_found']}")
    print(f"  Dominant period: {report['dominant_period']}")
    print(f"  Scales: {report['scales']}")
    print("  Top patterns:")
    for p in report["top_patterns"]:
        print(f"    period={p['period']}, strength={p['strength']}, scale={p['scale']}")
    return report


if __name__ == "__main__":
    demo()
