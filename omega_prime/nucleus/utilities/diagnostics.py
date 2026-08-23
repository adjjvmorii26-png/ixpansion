import time
from collections import defaultdict
from typing import Any


class Diagnostics:
    """Lightweight metrics and timing recorder."""

    def __init__(self) -> None:
        self._timings: dict[str, list[float]] = defaultdict(list)
        self._counters: dict[str, int] = defaultdict(int)

    def record_timing(self, name: str, ms: float) -> None:
        self._timings[name].append(ms)
        if len(self._timings[name]) > 200:
            self._timings[name] = self._timings[name][-200:]

    def increment(self, name: str) -> None:
        self._counters[name] += 1

    def avg_ms(self, name: str) -> float:
        vals = self._timings.get(name, [])
        return round(sum(vals) / len(vals), 2) if vals else 0.0

    def report(self) -> dict[str, Any]:
        return {
            "avg_timings_ms": {k: self.avg_ms(k) for k in self._timings},
            "counters": dict(self._counters),
        }
