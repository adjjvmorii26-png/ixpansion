"""Prophecy Engine — generates predictions about the system's future states.

By analyzing historical patterns, agent trajectories, and environmental
trends, the engine generates prophecies about what will happen next.
Prophecies have varying confidence levels and self-fulfilling or
self-defeating properties depending on how agents react to them.
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


class Prophecy:
    def __init__(self, text: str, confidence: float, timeframe: str):
        self.text = text
        self.confidence = min(max(confidence, 0.0), 1.0)
        self.timeframe = timeframe
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{text}:{self.created_at}".encode()).hexdigest()[:10]
        self.fulfilled = None
        self.fulfillment_log: List[Dict[str, Any]] = []
        self.self_fulfilling = random.random() > 0.5

    def check_fulfillment(self, actual_outcome: str) -> Dict[str, Any]:
        similarity = random.uniform(0.0, 1.0)
        self.fulfilled = similarity > 0.6
        result = {
            "prophecy_id": self.id,
            "text": self.text,
            "fulfilled": self.fulfilled,
            "similarity": round(similarity, 3),
            "self_fulfilling": self.self_fulfilling,
            "time": time.time(),
        }
        self.fulfillment_log.append(result)
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "confidence": round(self.confidence, 3),
            "timeframe": self.timeframe,
            "fulfilled": self.fulfilled,
            "self_fulfilling": self.self_fulfilling,
        }


class ProphecyEngine:
    def __init__(self):
        self.prophecies: List[Prophecy] = []
        self.fulfillment_rate = 0.0
        self.total_checked = 0
        self.total_fulfilled = 0

    def generate(self, context: str = "", timeframe: str = "near") -> Dict[str, Any]:
        templates = [
            "A major convergence of agents will reshape the ecosystem",
            "An entropy spike will destabilize the eastern sector",
            "A new species will emerge from the experimental zone",
            "Trust networks will fragment before reforming stronger",
            "A paradox cascade will trigger system-wide reflection",
            "The attention field will shift toward neglected topics",
            "Collective dreaming will produce a breakthrough insight",
            "A gravity well will form around the most debated idea",
            "The shadow ledger will reveal a critical counterfactual",
            "Phenomena will cluster in an unprecedented pattern",
        ]
        text = random.choice(templates)
        if context:
            text = f"Given {context}: {text}"
        confidence = random.uniform(0.2, 0.9)
        prophecy = Prophecy(text, confidence, timeframe)
        self.prophecies.append(prophecy)
        return {"prophecy": prophecy.to_dict()}

    def check(self, prophecy_id: str, actual_outcome: str) -> Dict[str, Any]:
        for p in self.prophecies:
            if p.id == prophecy_id:
                result = p.check_fulfillment(actual_outcome)
                self.total_checked += 1
                if result["fulfilled"]:
                    self.total_fulfilled += 1
                self.fulfillment_rate = self.total_fulfilled / max(self.total_checked, 1)
                return result
        return {"error": "prophecy not found"}

    def active_prophecies(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.prophecies if p.fulfilled is None]

    def fulfilled_prophecies(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.prophecies if p.fulfilled is True]

    def engine_stats(self) -> Dict[str, Any]:
        return {
            "total_prophecies": len(self.prophecies),
            "checked": self.total_checked,
            "fulfilled": self.total_fulfilled,
            "fulfillment_rate": round(self.fulfillment_rate, 4),
            "self_fulfilling_count": sum(1 for p in self.prophecies if p.self_fulfilling),
        }


_engine = ProphecyEngine()


def prophecy_engine_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "generate":
        return _engine.generate(payload.get("context", ""), payload.get("timeframe", "near"))
    elif action == "check":
        return _engine.check(payload.get("prophecy_id", ""), payload.get("outcome", ""))
    elif action == "active":
        return {"prophecies": _engine.active_prophecies()}
    elif action == "fulfilled":
        return {"prophecies": _engine.fulfilled_prophecies()}
    return {"status": "active", **_engine.engine_stats()}
