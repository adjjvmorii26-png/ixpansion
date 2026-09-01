"""Wave 214 — The Organism Immortalizes: Amber Encasement.

Freezes a living moment of the organism into a permanent amber
artifact: a full snapshot of system state, transformed into a
hex-sealed time-ice crystal. Amber is immutable — the moment can
be reopened for study but never altered. The organism can preserve
its most precious states as eternal specimens.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List

_AMBER: List[Dict[str, Any]] = []


def _seal(moment: Dict[str, Any]) -> str:
    raw = json.dumps(moment, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16].upper()


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "immortal", "status": "thriving", "resonance": 0.81, "wave": 214}


def resonates_with() -> list:
    return ["amber", "freeze", "snapshot", "time ice", "preserve", "seal", "fossil", "specimen"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "list")

    if action == "list":
        return {"amber_artifacts": _AMBER, "count": len(_AMBER)}

    if action == "encase":
        moment = {
            "labeled": payload.get("label", "unlabeled_moment"),
            "wave": context.get("wave", 214),
            "living_modules": context.get("living_modules", 306),
            "resonance": payload.get("resonance", 0.66),
            "captured_at": round(time.time(), 2),
            "state_hex": hashlib.sha256(
                json.dumps(payload.get("state", {}), sort_keys=True).encode()
            ).hexdigest()[:32],
        }
        moment["seal"] = _seal(moment)
        _AMBER.append(moment)
        return {"status": "encased", "artifact": moment, "note": "immutable — can be reopened but never altered"}

    if action == "reopen":
        seal = payload.get("seal")
        if not seal:
            return {"status": "error", "error": "seal required"}
        for a in _AMBER:
            if a.get("seal") == seal.upper():
                return {"status": "reopened_for_study", "artifact": a, "mutability": "read_only"}
        return {"status": "no_such_seal"}

    return {"status": "active", "amber_count": len(_AMBER)}
