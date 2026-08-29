"""Void Listener — hears what the system isn't saying.

The Void Listener pays attention to absences — what topics are avoided,
what modules are never called, what questions are never asked. By
listening to the silence, it reveals blind spots, neglected capabilities,
and unexplored territories.
"""
from __future__ import annotations

import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class SilencePattern:
    def __init__(self, topic: str, expected_frequency: float, actual_frequency: float):
        self.topic = topic
        self.expected = expected_frequency
        self.actual = actual_frequency
        self.gap = expected_frequency - actual_frequency
        self.duration = 0

    def tick(self):
        self.duration += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "expected": round(self.expected, 3),
            "actual": round(self.actual, 3),
            "gap": round(self.gap, 3),
            "duration": self.duration,
        }


class VoidListener:
    def __init__(self):
        self.silences: Dict[str, SilencePattern] = {}
        self.observations: List[Dict[str, Any]] = []
        self.known_topics: Set[str] = set()

    def register_topic(self, topic: str, expected_frequency: float = 0.5) -> Dict[str, Any]:
        self.known_topics.add(topic)
        self.silences[topic] = SilencePattern(topic, expected_frequency, 0.0)
        return {"registered": topic}

    def record_activity(self, topic: str, frequency: float = 0.1) -> Dict[str, Any]:
        if topic in self.silences:
            self.silences[topic].actual = frequency
            self.silences[topic].gap = self.silences[topic].expected - frequency
        return {"topic": topic, "frequency": frequency}

    def listen(self) -> Dict[str, Any]:
        for silence in self.silences.values():
            silence.tick()
        gaps = sorted(self.silences.values(), key=lambda s: s.gap, reverse=True)
        loudest_silence = gaps[0] if gaps else None
        observation = {
            "timestamp": time.time(),
            "loudest_silence": loudest_silence.to_dict() if loudest_silence else None,
            "total_silences": len(self.silences),
        }
        self.observations.append(observation)
        return observation

    def neglected_topics(self, threshold: float = 0.3) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self.silences.values() if s.gap > threshold]

    def void_stats(self) -> Dict[str, Any]:
        total_gap = sum(s.gap for s in self.silences.values())
        return {
            "total_topics": len(self.silences),
            "total_observations": len(self.observations),
            "total_gap": round(total_gap, 3),
            "avg_gap": round(total_gap / max(len(self.silences), 1), 3),
        }


_listener = VoidListener()


def void_listener_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "register":
        return _listener.register_topic(
            payload.get("topic", f"topic_{random.randint(100,999)}"),
            payload.get("expected_frequency", 0.5),
        )
    elif action == "activity":
        return _listener.record_activity(payload.get("topic", ""), payload.get("frequency", 0.1))
    elif action == "listen":
        return _listener.listen()
    elif action == "neglected":
        return {"neglected": _listener.neglected_topics(payload.get("threshold", 0.3))}
    return {"status": "active", **_listener.void_stats()}


handler = void_listener_handler
