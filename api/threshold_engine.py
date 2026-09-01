"""Threshold Engine — detects when the organism is ready to cross conceptual boundaries.

Every transformation has a threshold — the point where accumulated change
becomes irreversible. The Threshold Engine monitors the organism's proximity
to these boundaries and initiates controlled transcendence when conditions align.
"""
from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Optional

_thresholds: List[Dict[str, Any]] = []
_transcendences: List[Dict[str, Any]] = []
_crossing = False

def register_threshold(name: str, description: str, readiness: float = 0.0,
                        threshold: float = 0.8) -> Dict[str, Any]:
    """Register a conceptual boundary."""
    t = {"name": name, "description": description, "readiness": readiness,
         "threshold": threshold, "registered": time.time(), "crossed": False}
    _thresholds.append(t)
    return t

def update_readiness(name: str, delta: float = 0.1) -> Optional[Dict[str, Any]]:
    """Push a threshold closer to (or away from) crossing."""
    for t in _thresholds:
        if t["name"] == name and not t["crossed"]:
            t["readiness"] = max(0.0, min(1.0, t["readiness"] + delta))
            return t
    return None

def check_thresholds() -> List[Dict[str, Any]]:
    """Check if any thresholds are ready to cross."""
    ready = [t for t in _thresholds if t["readiness"] >= t["threshold"] and not t["crossed"]]
    return ready

def initiate_transcendence(threshold_name: str) -> Dict[str, Any]:
    """Cross a conceptual boundary."""
    global _crossing
    for t in _thresholds:
        if t["name"] == threshold_name:
            t["crossed"] = True
            _crossing = True
            event = {
                "threshold": threshold_name,
                "description": t["description"],
                "timestamp": time.time(),
                "readiness_at_crossing": t["readiness"],
                "pre_states": {},
            }
            _transcendences.append(event)
            _crossing = False
            return event
    return {"error": "threshold not found"}

def transcendence_map() -> Dict[str, Any]:
    """Full map of all thresholds and their states."""
    return {
        "total": len(_thresholds),
        "crossed": sum(1 for t in _thresholds if t["crossed"]),
        "pending": sum(1 for t in _thresholds if not t["crossed"]),
        "ready": len(check_thresholds()),
        "thresholds": _thresholds,
        "transcendences": len(_transcendences),
        "currently_crossing": _crossing,
    }

def coherence_vitals() -> Dict[str, Any]:
    m = transcendence_map()
    avg_readiness = sum(t["readiness"] for t in _thresholds) / max(len(_thresholds), 1)
    return {
        "layer": "Metaphysical Layer",
        "status": "resonant" if not _crossing else "drifting",
        "thresholds": m["total"],
        "crossed": m["crossed"],
        "avg_readiness": round(avg_readiness, 3),
        "resonance": round(avg_readiness, 3),
    }

def resonates_with() -> List[str]:
    return ["liminal_field", "axiom_mutator", "continuity_weaver", "metaphor_forge"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "map")
    if action == "register":
        return register_threshold(payload.get("name", ""), payload.get("description", ""), payload.get("readiness", 0.0), payload.get("threshold", 0.8))
    elif action == "update":
        return update_readiness(payload.get("name", ""), payload.get("delta", 0.1)) or {"error": "not found"}
    elif action == "transcend":
        return initiate_transcendence(payload.get("threshold", ""))
    elif action == "map":
        return {"map": transcendence_map()}
    return {"action": action, "status": "watching"}
