"""Attention Field — models collective focus as a physical field.

The system has a measurable "attention field" — the sum of all agent
focus. Attention flows toward interesting things, pools in some areas,
and starves others. This creates natural prioritization without central
planning.
"""
from __future__ import annotations

import math
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class FocusPoint:
    def __init__(self, topic: str, x: float = 0.0, y: float = 0.0):
        self.topic = topic
        self.x = x
        self.y = y
        self.attention = 0.0
        self.attractors: List[str] = []
        self.created_at = time.time()

    def attract(self, amount: float):
        self.attention += amount

    def decay(self, rate: float = 0.05):
        self.attention *= (1.0 - rate)

    def distance_to(self, other: "FocusPoint") -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "position": [round(self.x, 2), round(self.y, 2)],
            "attention": round(self.attention, 4),
            "age": round(time.time() - self.created_at, 1),
        }


class AttentionField:
    def __init__(self):
        self.points: Dict[str, FocusPoint] = {}
        self.total_attention_emitted = 0.0
        self.history: List[Dict[str, Any]] = []
        self._tick = 0

    def create_point(self, topic: str, x: float = None, y: float = None) -> Dict[str, Any]:
        point = FocusPoint(topic, x or random.uniform(-10, 10), y or random.uniform(-10, 10))
        self.points[topic] = point
        return {"created": point.to_dict()}

    def direct_attention(self, agent_id: str, topic: str, amount: float = 1.0) -> Dict[str, Any]:
        if topic not in self.points:
            self.create_point(topic)
        self.points[topic].attract(amount)
        self.total_attention_emitted += amount
        self._propagate(topic, amount * 0.3)
        return {
            "agent": agent_id,
            "topic": topic,
            "directed": amount,
            "total_attention_on_topic": round(self.points[topic].attention, 4),
        }

    def _propagate(self, source_topic: str, amount: float):
        source = self.points.get(source_topic)
        if not source:
            return
        for topic, point in self.points.items():
            if topic == source_topic:
                continue
            dist = source.distance_to(point)
            if dist < 5.0:
                propagated = amount * (1.0 - dist / 5.0)
                point.attract(propagated)

    def tick(self) -> Dict[str, Any]:
        """Decay all attention and record snapshot."""
        self._tick += 1
        for point in self.points.values():
            point.decay()
        hotspots = sorted(
            self.points.values(), key=lambda p: p.attention, reverse=True
        )[:3]
        snapshot = {
            "tick": self._tick,
            "hotspots": [p.topic for p in hotspots if p.attention > 0],
            "total_attention": round(sum(p.attention for p in self.points.values()), 2),
        }
        self.history.append(snapshot)
        return snapshot

    def field_map(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.points.values()]

    def starved_topics(self, threshold: float = 0.1) -> List[str]:
        return [p.topic for p in self.points.values() if p.attention < threshold]

    def field_stats(self) -> Dict[str, Any]:
        return {
            "total_points": len(self.points),
            "total_attention_emitted": round(self.total_attention_emitted, 4),
            "current_total": round(sum(p.attention for p in self.points.values()), 4),
            "ticks": self._tick,
            "starved_count": len(self.starved_topics()),
        }


_field = AttentionField()


def attention_field_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "create":
        return _field.create_point(
            payload.get("topic", "unknown"),
            payload.get("x"), payload.get("y"),
        )
    elif action == "direct":
        return _field.direct_attention(
            payload.get("agent_id", "observer"),
            payload.get("topic", ""),
            payload.get("amount", 1.0),
        )
    elif action == "tick":
        return _field.tick()
    elif action == "map":
        return {"map": _field.field_map()}
    elif action == "starved":
        return {"starved": _field.starved_topics(payload.get("threshold", 0.1))}
    return {"status": "active", **_field.field_stats()}


handler = attention_field_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "attention_field"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "attention_field", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
