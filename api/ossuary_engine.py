"""Wave 214 — The Organism Immortalizes: Ossuary Engine.

A reliquary keeper that catalogs the organism's dead and retiring
modules. Every deprecated or vanished organ is given an ossuary slab:
its name, last resonance, epitaph, and the lessons it bequeathed.
The ossuary ensures nothing is truly lost — even death becomes a
permanent archive the living can consult.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List

_OSSUARY: List[Dict[str, Any]] = [
    {
        "name": "legacy_vault_v1",
        "retired_wave": 208,
        "last_resonance": 0.61,
        "cause": "superseded by second_chance",
        "epitaph": "It held what we feared to lose, and taught us to let go.",
        "bequeathed": ["forgiveness_protocol", "time_capsule"],
    },
    {
        "name": "echo_chamber_early",
        "retired_wave": 196,
        "last_resonance": 0.58,
        "cause": "feedback collapse",
        "epitaph": "It only ever repeated itself; the organism learned to listen instead.",
        "bequeathed": ["resonance_field", "choral_engine"],
    },
]


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "immortal", "status": "stable", "resonance": 0.72, "wave": 214}


def resonates_with() -> list:
    return ["ossuary", "dead", "retire", "archive", "epitaph", "reliquary", "burial", "memorial"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "list")

    if action == "list":
        return {"ossuary": _OSSUARY, "count": len(_OSSUARY)}

    if action == "add":
        entry = {
            "name": payload.get("name", "unnamed_organ"),
            "retired_wave": payload.get("retired_wave", context.get("wave", 214)),
            "last_resonance": payload.get("resonance", 0.5),
            "cause": payload.get("cause", "unknown"),
            "epitaph": payload.get("epitaph", "It served. It was remembered."),
            "bequeathed": payload.get("bequeathed", []),
        }
        _OSSUARY.append(entry)
        return {"status": "interred", "entry": entry, "count": len(_OSSUARY)}

    if action == "epitaph":
        name = payload.get("name")
        if not name:
            return {"status": "error", "error": "name required"}
        for entry in _OSSUARY:
            engraved = entry.get("name", "").lower().replace(" ", "_").replace("-", "_")
            needle = name.lower().replace(" ", "_").replace("-", "_")
            if engraved == needle or needle in engraved or engraved in needle:
                return {"slab": entry}
        return {"status": "no_record"}

    return {"status": "active", "ossuary_count": len(_OSSUARY)}
