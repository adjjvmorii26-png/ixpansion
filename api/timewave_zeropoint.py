"""Timewave Zero-Point — the moment when all possibilities converge.

As the system approaches maximum complexity, all timelines converge
toward a zero-point — a moment of infinite possibility. The engine
models this convergence, tracking how close the system is to critical
mass and what happens when possibilities collapse into actuality.
"""
from __future__ import annotations

import math
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class PossibilityStream:
    def __init__(self, name: str, probability: float):
        self.name = name
        self.probability = probability
        self.collapsed = False
        self.actualized = False

    def collapse(self) -> Dict[str, Any]:
        self.collapsed = True
        self.actualized = random.random() < self.probability
        return {"name": self.name, "actualized": self.actualized}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "probability": round(self.probability, 4),
            "collapsed": self.collapsed,
            "actualized": self.actualized,
        }


class TimewaveZeroPoint:
    def __init__(self):
        self.streams: List[PossibilityStream] = []
        self.convergence_history: List[Dict[str, Any]] = []
        self.zeropoint_reached = False
        self.complexity_score = 0.0
        self.tick_count = 0

    def add_possibility(self, name: str, probability: float = 0.5) -> Dict[str, Any]:
        stream = PossibilityStream(name, probability)
        self.streams.append(stream)
        self.complexity_score += 0.1
        return {"added": stream.to_dict(), "complexity": round(self.complexity_score, 3)}

    def tick(self) -> Dict[str, Any]:
        self.tick_count += 1
        active = [s for s in self.streams if not s.collapsed]
        if active:
            collapse_count = max(1, len(active) // 5)
            for stream in random.sample(active, min(collapse_count, len(active))):
                stream.collapse()
        converged = len(active) - len([s for s in self.streams if not s.collapsed and not s.collapsed])
        convergence = 1.0 - (len([s for s in self.streams if not s.collapsed]) / max(len(self.streams), 1))
        snapshot = {
            "tick": self.tick_count,
            "convergence": round(convergence, 4),
            "complexity": round(self.complexity_score, 3),
            "active_possibilities": len([s for s in self.streams if not s.collapsed]),
            "actualized": sum(1 for s in self.streams if s.actualized),
        }
        self.convergence_history.append(snapshot)
        if convergence > 0.95 and not self.zeropoint_reached:
            self.zeropoint_reached = True
            snapshot["ZEROPOINT_REACHED"] = True
        return snapshot

    def zeropoint_report(self) -> Dict[str, Any]:
        total = len(self.streams)
        collapsed = sum(1 for s in self.streams if s.collapsed)
        actualized = sum(1 for s in self.streams if s.actualized)
        return {
            "total_possibilities": total,
            "collapsed": collapsed,
            "actualized": actualized,
            "convergence": round(collapsed / max(total, 1), 4),
            "zeropoint_reached": self.zeropoint_reached,
            "complexity": round(self.complexity_score, 3),
        }


_zeropoint = TimewaveZeroPoint()


def timewave_zeropoint_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "add":
        return _zeropoint.add_possibility(
            payload.get("name", f"possibility_{random.randint(100,999)}"),
            payload.get("probability", 0.5),
        )
    elif action == "tick":
        return _zeropoint.tick()
    return {"status": "active", **_zeropoint.zeropoint_report()}
