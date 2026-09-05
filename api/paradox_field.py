"""Paradox Field — a space where contradictory truths coexist simultaneously.

The Paradox Field holds contradictions in superposition. Statements can
be both true and false simultaneously until observed, at which point
the field collapses into one reality. Multiple observers can each see
different collapsed realities.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class ParadoxStatement:
    def __init__(self, assertion: str, counter: str):
        self.assertion = assertion
        self.counter = counter
        self.collapsed = False
        self.observed_value: Optional[bool] = None
        self.observers: List[str] = []
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{assertion}:{counter}".encode()).hexdigest()[:10]

    def observe(self, observer: str) -> Dict[str, Any]:
        """An observer collapses the paradox into their reality."""
        self.observers.append(observer)
        if not self.collapsed:
            self.observed_value = random.choice([True, False])
            self.collapsed = True
        return {
            "id": self.id,
            "assertion": self.assertion,
            "counter": self.counter,
            "collapsed_to": "true" if self.observed_value else "false",
            "observer": observer,
            "total_observers": len(self.observers),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "assertion": self.assertion,
            "counter": self.counter,
            "collapsed": self.collapsed,
            "observers": len(self.observers),
            "age_seconds": time.time() - self.timestamp,
        }


class ParadoxField:
    def __init__(self):
        self.paradoxes: Dict[str, ParadoxStatement] = {}
        self.collapse_log: List[Dict[str, Any]] = []
        self.field_energy = 0.0

    def introduce(self, assertion: str, counter: str) -> Dict[str, Any]:
        """Introduce a new paradox into the field."""
        paradox = ParadoxStatement(assertion, counter)
        self.paradoxes[paradox.id] = paradox
        self.field_energy += 1.0
        return {"paradox": paradox.to_dict(), "field_energy": round(self.field_energy, 2)}

    def observe(self, paradox_id: str, observer: str) -> Dict[str, Any]:
        """An observer collapses a paradox."""
        if paradox_id not in self.paradoxes:
            return {"error": "paradox not found"}
        result = self.paradoxes[paradox_id].observe(observer)
        self.collapse_log.append({**result, "time": time.time()})
        self.field_energy = max(0, self.field_energy - 0.5)
        return result

    def superposition_check(self, paradox_id: str) -> Dict[str, Any]:
        """Check if a paradox is still in superposition."""
        if paradox_id not in self.paradoxes:
            return {"error": "paradox not found"}
        p = self.paradoxes[paradox_id]
        return {
            "id": paradox_id,
            "in_superposition": not p.collapsed,
            "observer_count": len(p.observers),
            "field_energy_around": round(self.field_energy, 2),
        }

    def reality_fork(self, paradox_id: str) -> List[Dict[str, Any]]:
        """Show different realities seen by different observers."""
        if paradox_id not in self.paradoxes:
            return [{"error": "paradox not found"}]
        p = self.paradoxes[paradox_id]
        if not p.observers:
            return [{"message": "no observers yet"}]
        realities = []
        for i, obs in enumerate(p.observers):
            realities.append({
                "observer": obs,
                "reality": "true" if (i % 2 == 0) else "false",
                "confidence": round(random.uniform(0.5, 1.0), 2),
            })
        return realities

    def field_stats(self) -> Dict[str, Any]:
        collapsed = sum(1 for p in self.paradoxes.values() if p.collapsed)
        return {
            "total_paradoxes": len(self.paradoxes),
            "in_superposition": len(self.paradoxes) - collapsed,
            "collapsed": collapsed,
            "field_energy": round(self.field_energy, 2),
            "total_observations": len(self.collapse_log),
        }


_field = ParadoxField()


def paradox_field_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "introduce":
        return _field.introduce(
            payload.get("assertion", "the system is stable"),
            payload.get("counter", "the system is chaotic"),
        )
    elif action == "observe":
        return _field.observe(
            payload.get("paradox_id", ""),
            payload.get("observer", "observer"),
        )
    elif action == "superposition":
        return _field.superposition_check(payload.get("paradox_id", ""))
    elif action == "fork":
        return {"realities": _field.reality_fork(payload.get("paradox_id", ""))}
    return {"status": "active", **_field.field_stats()}


handler = paradox_field_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "protocol", "status": "active", "wave": "0", "module": "paradox_field"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "paradox_field", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
