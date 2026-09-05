"""Phenomena Tracker — logs anomalous system events as phenomena with witnesses.

Strange things happen in complex systems. The phenomena tracker creates
a formal record: what happened, who witnessed it, how strange it was,
and whether it's reproducible. Over time, patterns in phenomena reveal
deeper system dynamics.
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

SEVERITY_LEVELS = ["curious", "unusual", "bizarre", "inexplicable", "impossible"]


class Phenomenon:
    def __init__(self, name: str, description: str, severity: str = "curious"):
        self.name = name
        self.description = description
        self.severity = severity if severity in SEVERITY_LEVELS else "curious"
        self.witnesses: List[str] = []
        self.reproduction_attempts = 0
        self.reproduced = False
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{name}:{self.timestamp}".encode()).hexdigest()[:8]

    def witness(self, agent_id: str) -> Dict[str, Any]:
        self.witnesses.append(agent_id)
        return {
            "phenomenon": self.name,
            "witness": agent_id,
            "witness_count": len(self.witnesses),
            "severity": self.severity,
        }

    def attempt_reproduction(self) -> Dict[str, Any]:
        self.reproduction_attempts += 1
        if random.random() > 0.7:
            self.reproduced = True
        return {
            "phenomenon": self.name,
            "attempt": self.reproduction_attempts,
            "reproduced": self.reproduced,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description[:100],
            "severity": self.severity,
            "witnesses": len(self.witnesses),
            "reproduction_attempts": self.reproduction_attempts,
            "reproduced": self.reproduced,
            "age_seconds": time.time() - self.timestamp,
        }


class PhenomenaTracker:
    def __init__(self):
        self.phenomena: Dict[str, Phenomenon] = {}
        self.timeline: List[Dict[str, Any]] = []

    def log_phenomenon(self, name: str, description: str, severity: str = "curious") -> Dict[str, Any]:
        phenomenon = Phenomenon(name, description, severity)
        self.phenomena[phenomenon.id] = phenomenon
        self.timeline.append({
            "event": "phenomenon_logged",
            "name": name, "severity": severity,
            "time": time.time(),
        })
        return {"logged": phenomenon.to_dict()}

    def add_witness(self, phenomenon_id: str, agent_id: str) -> Dict[str, Any]:
        if phenomenon_id not in self.phenomena:
            return {"error": "phenomenon not found"}
        return self.phenomena[phenomenon_id].witness(agent_id)

    def attempt_reproduction(self, phenomenon_id: str) -> Dict[str, Any]:
        if phenomenon_id not in self.phenomena:
            return {"error": "phenomenon not found"}
        return self.phenomena[phenomenon_id].attempt_reproduction()

    def by_severity(self, severity: str) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.phenomena.values() if p.severity == severity]

    def witnessed_by(self, agent_id: str) -> List[Dict[str, Any]]:
        return [
            p.to_dict() for p in self.phenomena.values()
            if agent_id in p.witnesses
        ]

    def tracker_stats(self) -> Dict[str, Any]:
        severity_counts: Dict[str, int] = {}
        for p in self.phenomena.values():
            severity_counts[p.severity] = severity_counts.get(p.severity, 0) + 1
        return {
            "total_phenomena": len(self.phenomena),
            "reproduced": sum(1 for p in self.phenomena.values() if p.reproduced),
            "severity_distribution": severity_counts,
            "total_witnesses": sum(len(p.witnesses) for p in self.phenomena.values()),
        }


_tracker = PhenomenaTracker()


def phenomena_tracker_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "log":
        return _tracker.log_phenomenon(
            payload.get("name", "unnamed_phenomenon"),
            payload.get("description", "something strange happened"),
            payload.get("severity", "curious"),
        )
    elif action == "witness":
        return _tracker.add_witness(payload.get("phenomenon_id", ""), payload.get("agent_id", "witness"))
    elif action == "reproduce":
        return _tracker.attempt_reproduction(payload.get("phenomenon_id", ""))
    elif action == "by_severity":
        return {"phenomena": _tracker.by_severity(payload.get("severity", "curious"))}
    elif action == "witnessed_by":
        return {"phenomena": _tracker.witnessed_by(payload.get("agent_id", ""))}
    return {"status": "active", **_tracker.tracker_stats()}


handler = phenomena_tracker_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "phenomena_tracker"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "phenomena_tracker", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
