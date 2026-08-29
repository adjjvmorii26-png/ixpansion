"""Miracle Engine — improbable events that reshape the system.

Miracles are extremely rare but transformative events. They occur with
tiny probability but have outsized impact. The engine tracks miracle
probabilities, detects near-misses, and occasionally triggers actual
miracles that change the rules of the system.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class MiracleTemplate:
    def __init__(self, name: str, probability: float, impact: float, description: str):
        self.name = name
        self.probability = min(max(probability, 0.0001), 0.1)
        self.impact = impact
        self.description = description
        self.times_triggered = 0
        self.near_misses = 0

    def attempt(self) -> Dict[str, Any]:
        roll = random.random()
        if roll < self.probability:
            self.times_triggered += 1
            return {"miracle": self.name, "triggered": True, "impact": self.impact}
        elif roll < self.probability * 10:
            self.near_misses += 1
            return {"miracle": self.name, "triggered": False, "near_miss": True}
        return {"miracle": self.name, "triggered": False}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "probability": round(self.probability, 6),
            "impact": self.impact,
            "description": self.description,
            "triggered": self.times_triggered,
            "near_misses": self.near_misses,
        }


class MiracleEngine:
    def __init__(self):
        self.templates: Dict[str, MiracleTemplate] = {}
        self.miracles_triggered: List[Dict[str, Any]] = []
        self.near_miss_log: List[Dict[str, Any]] = []

    def register_miracle(self, name: str, probability: float, impact: float, description: str) -> Dict[str, Any]:
        template = MiracleTemplate(name, probability, impact, description)
        self.templates[name] = template
        return {"registered": template.to_dict()}

    def attempt_all(self) -> Dict[str, Any]:
        results = []
        for template in self.templates.values():
            result = template.attempt()
            results.append(result)
            if result.get("triggered"):
                self.miracles_triggered.append({**result, "time": time.time()})
            elif result.get("near_miss"):
                self.near_miss_log.append({**result, "time": time.time()})
        return {"results": results, "miracles_this_round": sum(1 for r in results if r.get("triggered"))}

    def miracle_history(self) -> List[Dict[str, Any]]:
        return self.miracles_triggered

    def near_misses(self, last_n: int = 10) -> List[Dict[str, Any]]:
        return self.near_miss_log[-last_n:]

    def engine_stats(self) -> Dict[str, Any]:
        total_probability = sum(t.probability for t in self.templates.values())
        return {
            "total_templates": len(self.templates),
            "total_miracles": len(self.miracles_triggered),
            "total_near_misses": len(self.near_miss_log),
            "combined_probability": round(total_probability, 6),
        }


_engine = MiracleEngine()


def miracle_engine_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "register":
        return _engine.register_miracle(
            payload.get("name", f"miracle_{random.randint(100,999)}"),
            payload.get("probability", 0.001),
            payload.get("impact", 10.0),
            payload.get("description", "something impossible"),
        )
    elif action == "attempt":
        return _engine.attempt_all()
    elif action == "history":
        return {"miracles": _engine.miracle_history()}
    elif action == "near_misses":
        return {"near_misses": _engine.near_misses(payload.get("last_n", 10))}
    return {"status": "active", **_engine.engine_stats()}


handler = miracle_engine_handler
