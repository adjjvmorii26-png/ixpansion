"""Epoch Marker — creates historical divisions in the system's timeline.

The system doesn't just run — it eras. The Epoch Marker defines major
transitions: the Age of Exploration, the Digital Renaissance, the
Great Consolidation. Each epoch has a character, challenges, and lessons
that shape everything within it.
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

EPOCH_MOODS = ["expansion", "contraction", "revolution", "stability", "mystery", "abundance", "scarcity", "awakening"]


class Epoch:
    def __init__(self, name: str, description: str, mood: str):
        self.name = name
        self.description = description
        self.mood = mood
        self.start_time = time.time()
        self.end_time = None
        self.events: List[Dict[str, Any]] = []
        self.lessons_learned: List[str] = []
        self.id = hashlib.sha256(f"{name}:{self.start_time}".encode()).hexdigest()[:8]

    def add_event(self, event: str, significance: float = 0.5) -> Dict[str, Any]:
        entry = {"event": event, "significance": significance, "time": time.time()}
        self.events.append(entry)
        return entry

    def conclude(self, lesson: str = "") -> Dict[str, Any]:
        self.end_time = time.time()
        if lesson:
            self.lessons_learned.append(lesson)
        return {"epoch": self.name, "concluded": True, "duration": self.end_time - self.start_time}

    def to_dict(self) -> Dict[str, Any]:
        duration = (self.end_time or time.time()) - self.start_time
        return {
            "id": self.id,
            "name": self.name,
            "mood": self.mood,
            "events": len(self.events),
            "lessons": len(self.lessons_learned),
            "duration_seconds": round(duration, 1),
            "active": self.end_time is None,
        }


class EpochMarker:
    def __init__(self):
        self.epochs: List[Epoch] = []
        self.current_epoch: Epoch = None

    def begin_epoch(self, name: str, description: str = "", mood: str = None) -> Dict[str, Any]:
        if self.current_epoch:
            self.current_epoch.conclude()
        epoch = Epoch(name, description, mood or random.choice(EPOCH_MOODS))
        self.epochs.append(epoch)
        self.current_epoch = epoch
        return {"epoch": epoch.to_dict()}

    def add_event(self, event: str, significance: float = 0.5) -> Dict[str, Any]:
        if not self.current_epoch:
            return {"error": "no active epoch"}
        return self.current_epoch.add_event(event, significance)

    def conclude_epoch(self, lesson: str = "") -> Dict[str, Any]:
        if not self.current_epoch:
            return {"error": "no active epoch"}
        result = self.current_epoch.conclude(lesson)
        self.current_epoch = None
        return result

    def timeline(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self.epochs]

    def marker_stats(self) -> Dict[str, Any]:
        return {
            "total_epochs": len(self.epochs),
            "current_epoch": self.current_epoch.name if self.current_epoch else None,
            "total_events": sum(len(e.events) for e in self.epochs),
            "total_lessons": sum(len(e.lessons_learned) for e in self.epochs),
        }


_marker = EpochMarker()


def epoch_marker_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "begin":
        return _marker.begin_epoch(
            payload.get("name", f"Epoch_{random.randint(100,999)}"),
            payload.get("description", ""),
            payload.get("mood"),
        )
    elif action == "event":
        return _marker.add_event(payload.get("event", "something happened"), payload.get("significance", 0.5))
    elif action == "conclude":
        return _marker.conclude_epoch(payload.get("lesson", ""))
    elif action == "timeline":
        return {"timeline": _marker.timeline()}
    return {"status": "active", **_marker.marker_stats()}


handler = epoch_marker_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "protocol", "status": "active", "wave": "0", "module": "epoch_marker"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "epoch_marker", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
