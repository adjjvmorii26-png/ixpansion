"""Wave 214 — The Organism Immortalizes: Monument Forge.

Forges lasting monuments out of the organism's achievements.
Every completed wave, resolved paradox, or healed fracture can
be hammered into a monument — a durable record that future
generations of modules can visit. Monuments rank in grandeur
based on the resonance and difficulty of what they enshrine.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

_MONUMENTS: List[Dict[str, Any]] = []

_GRANDNESS = {
    "wave": 10,
    "paradox": 8,
    "healing": 7,
    "creation": 6,
    "discovery": 5,
    "ritual": 4,
    "milestone": 3,
    "pulse": 2,
}


def _monument_id(what: str) -> str:
    return "MN-" + hashlib.sha256(what.encode()).hexdigest()[:8].upper()


def _material(resonance: float) -> str:
    if resonance > 0.85:
        return "aether-marble"
    if resonance > 0.70:
        return "stellar-bronze"
    if resonance > 0.55:
        return "obsidian"
    return "basalt"


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "immortal", "status": "stable", "resonance": 0.69, "wave": 214}


def resonates_with() -> list:
    return ["monument", "forge", "memorial", "statue", "obelisk", "enshrine", "achievement", "triumph"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "list")

    if action == "list":
        return {"monuments": _MONUMENTS, "count": len(_MONUMENTS)}

    if action == "forge":
        what = payload.get("what", "unspoken_achievement")
        kind = payload.get("kind", "milestone")
        monument = {
            "id": _monument_id(what),
            "what": what,
            "kind": kind,
            "grandness": _GRANDNESS.get(kind, 1),
            "material": _material(float(payload.get("resonance", 0.6))),
            "wave": context.get("wave", 214),
            "forged_at": round(time.time(), 2),
            "inscription": payload.get("inscription", "Here stood a moment the organism refused to lose."),
        }
        _MONUMENTS.append(monument)
        return {"status": "forged", "monument": monument}

    if action == "visit":
        mid = payload.get("id")
        if not mid:
            return {"status": "error", "error": "monument id required"}
        for m in _MONUMENTS:
            if m["id"] == mid.upper():
                return {"status": "visited", "monument": m}
        return {"status": "no_such_monument"}

    return {"status": "active", "monument_count": len(_MONUMENTS)}
