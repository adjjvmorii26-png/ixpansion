"""ChronoSync — synchronizes events across different time streams.

The system runs multiple parallel time streams at different speeds.
ChronoSync keeps them aligned by detecting drift, inserting sync points,
and resolving temporal paradoxes when streams diverge too far.
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


class TimeStream:
    def __init__(self, name: str, speed: float = 1.0):
        self.name = name
        self.speed = speed
        self.current_tick = 0
        self.events: List[Dict[str, Any]] = []
        self.drift = 0.0
        self.created_at = time.time()

    def advance(self, ticks: int = 1) -> Dict[str, Any]:
        actual_ticks = int(ticks * self.speed)
        self.current_tick += actual_ticks
        self.drift += abs(actual_ticks - ticks) * 0.01
        return {"stream": self.name, "tick": self.current_tick, "drift": round(self.drift, 4)}

    def record_event(self, event: str) -> Dict[str, Any]:
        entry = {"event": event, "tick": self.current_tick, "time": time.time()}
        self.events.append(entry)
        return entry

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "speed": self.speed,
            "tick": self.current_tick,
            "drift": round(self.drift, 4),
            "events": len(self.events),
        }


class ChronoSync:
    def __init__(self):
        self.streams: Dict[str, TimeStream] = {}
        self.sync_points: List[Dict[str, Any]] = []
        self.paradoxes: List[Dict[str, Any]] = []

    def create_stream(self, name: str, speed: float = 1.0) -> Dict[str, Any]:
        stream = TimeStream(name, speed)
        self.streams[name] = stream
        return {"created": stream.to_dict()}

    def advance_stream(self, name: str, ticks: int = 1) -> Dict[str, Any]:
        if name not in self.streams:
            return {"error": "stream not found"}
        return self.streams[name].advance(ticks)

    def sync_all(self) -> Dict[str, Any]:
        reference = max(self.streams.values(), key=lambda s: s.current_tick) if self.streams else None
        if not reference:
            return {"error": "no streams"}
        sync_point = {
            "reference_tick": reference.current_tick,
            "streams": {},
            "max_drift": 0.0,
            "timestamp": time.time(),
        }
        for name, stream in self.streams.items():
            drift = abs(stream.current_tick - reference.current_tick)
            sync_point["streams"][name] = {
                "tick": stream.current_tick,
                "drift_from_reference": drift,
            }
            sync_point["max_drift"] = max(sync_point["max_drift"], drift)
        if sync_point["max_drift"] > 10:
            self.paradoxes.append({
                "type": "temporal_divergence",
                "max_drift": sync_point["max_drift"],
                "time": time.time(),
            })
        self.sync_points.append(sync_point)
        return sync_point

    def detect_paradoxes(self) -> List[Dict[str, Any]]:
        return [p for p in self.paradoxes]

    def stream_comparison(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self.streams.values()]

    def stats(self) -> Dict[str, Any]:
        return {
            "total_streams": len(self.streams),
            "total_sync_points": len(self.sync_points),
            "total_paradoxes": len(self.paradoxes),
            "total_events": sum(len(s.events) for s in self.streams.values()),
        }


_chrono = ChronoSync()


def chronosync_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "create":
        return _chrono.create_stream(
            payload.get("name", f"stream_{random.randint(100,999)}"),
            payload.get("speed", 1.0),
        )
    elif action == "advance":
        return _chrono.advance_stream(payload.get("name", ""), payload.get("ticks", 1))
    elif action == "sync":
        return _chrono.sync_all()
    elif action == "paradoxes":
        return {"paradoxes": _chrono.detect_paradoxes()}
    elif action == "compare":
        return {"streams": _chrono.stream_comparison()}
    return {"status": "active", **_chrono.stats()}


handler = chronosync_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "organ", "status": "active", "wave": "0", "module": "chronosync"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "chronosync", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
