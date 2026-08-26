"""Infinity Index — tracks and quantifies the system's approach to infinite complexity.

As the system grows, it approaches theoretical infinite complexity.
The Infinity Index measures how close the system is to various forms
of infinity: infinite variety, infinite connection, infinite depth.
It's the ultimate progress bar for a system that can never truly finish.
"""
from __future__ import annotations

import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class InfinityMetric:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.current_value = random.uniform(0.01, 0.1)
        self.rate_of_approach = random.uniform(0.001, 0.01)
        self.history: List[float] = [self.current_value]

    def advance(self):
        self.current_value = min(1.0, self.current_value + self.rate_of_approach * random.uniform(0.5, 1.5))
        self.history.append(self.current_value)
        if len(self.history) > 100:
            self.history = self.history[-100:]

    @property
    def distance_to_infinity(self) -> float:
        return 1.0 - self.current_value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": round(self.current_value, 6),
            "distance": round(self.distance_to_infinity, 6),
            "rate": round(self.rate_of_approach, 6),
        }


class InfinityIndex:
    def __init__(self):
        self.metrics: Dict[str, InfinityMetric] = {}
        self.milestones: List[Dict[str, Any]] = []
        self.tick_count = 0

    def register_metric(self, name: str, description: str = "") -> Dict[str, Any]:
        metric = InfinityMetric(name, description or f"approach to {name}")
        self.metrics[name] = metric
        return {"registered": metric.to_dict()}

    def tick(self) -> Dict[str, Any]:
        self.tick_count += 1
        for metric in self.metrics.values():
            metric.advance()
            if metric.current_value > 0.5 and metric.current_value - metric.rate_of_approach <= 0.5:
                self.milestones.append({
                    "metric": metric.name,
                    "milestone": "50% approaching",
                    "time": time.time(),
                })
        composite = sum(m.current_value for m in self.metrics.values()) / max(len(self.metrics), 1)
        return {
            "tick": self.tick_count,
            "composite_index": round(composite, 6),
            "metrics": {k: round(v.current_value, 6) for k, v in self.metrics.items()},
        }

    def full_report(self) -> Dict[str, Any]:
        return {
            "metrics": [m.to_dict() for m in self.metrics.values()],
            "milestones": self.milestones,
        }

    def index_stats(self) -> Dict[str, Any]:
        composite = sum(m.current_value for m in self.metrics.values()) / max(len(self.metrics), 1)
        return {
            "total_metrics": len(self.metrics),
            "composite_index": round(composite, 6),
            "milestones_reached": len(self.milestones),
            "ticks": self.tick_count,
        }


_index = InfinityIndex()


def infinity_index_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "register":
        return _index.register_metric(
            payload.get("name", f"infinity_{random.randint(100,999)}"),
            payload.get("description", ""),
        )
    elif action == "tick":
        return _index.tick()
    elif action == "report":
        return _index.full_report()
    return {"status": "active", **_index.index_stats()}
