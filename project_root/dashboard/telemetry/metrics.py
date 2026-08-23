import time
from collections import defaultdict
from typing import Any


class MetricsCollector:
    """In-memory metrics store with rolling averages."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._timings: dict[str, list[float]] = defaultdict(list)

    def increment(self, name: str, amount: int = 1) -> None:
        self._counters[name] += amount

    def gauge(self, name: str, value: float) -> None:
        self._gauges[name] = value

    def timing(self, name: str, duration_ms: float) -> None:
        self._timings[name].append(duration_ms)
        if len(self._timings[name]) > 100:
            self._timings[name] = self._timings[name][-100:]

    def avg_timing(self, name: str) -> float:
        vals = self._timings.get(name, [])
        return sum(vals) / len(vals) if vals else 0.0

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "avg_timings_ms": {k: round(self.avg_timing(k), 2) for k in self._timings},
        }
