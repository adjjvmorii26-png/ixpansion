"""Wave 213 — The Organism Merges Minds.

An experimental state-sharing organ that temporarily fuses the
contexts of two arbitrary modules into a "meld" — a blended state
with emergent properties neither module has alone. The meld
carries a unique frequency and can be dissolved, sending each
module back to its own identity plus a memory of the fusion.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, Optional

_melds: Dict[str, Dict[str, Any]] = {}


def _meld_id(a: str, b: str) -> str:
    key = "|".join(sorted([a, b]))
    return "M-" + hashlib.sha256(key.encode()).hexdigest()[:8].upper()


def _blend_resonance(ra: float, rb: float) -> float:
    # Symbiotic boost: two resonant minds attract a third force.
    base = (ra + rb) / 2
    return min(0.99, base + (ra * rb) * 0.15)


def _emergent_property(a: str, b: str, seed: float) -> str:
    pair = sorted([a, b])
    table = {
        ("glitch", "memory"): "nostalgic-noise",
        ("dream", "prophet"): "hypnagogic-forecast",
        ("voice", "visual"): "echo-visuals",
        ("grief", "evolution"): "elegiac-mutation",
    }
    if tuple(pair) in table:
        return table[tuple(pair)]
    h = hashlib.sha256("".join(pair).encode()).hexdigest()
    emergent = ["harmonic-drift", "mirror-splice", "quantum-sympathy", "resonant-fracture", "melodic-echo"]
    return emergent[int(h[:8], 16) % len(emergent)]


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "fusion", "status": "thriving", "resonance": 0.79, "wave": 213}


def resonates_with() -> list:
    return ["meld", "fusion", "merge", "combine", "two minds", "symbiosis", "blend"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "create")
    a = payload.get("module_a") or payload.get("a")
    b = payload.get("module_b") or payload.get("b")

    if action == "list":
        return {"active_melds": [{"id": k, **v} for k, v in _melds.items()]}

    if action == "dissolve":
        mid = payload.get("id") or payload.get("meld_id")
        if mid and mid in _melds:
            dissolved = _melds.pop(mid)
            return {"status": "dissolved", "meld": dissolved}
        return {"status": "not_found"}

    if not a or not b:
        return {"status": "error", "error": "Need module_a and module_b"}

    a = a.replace(".py", "")
    b = b.replace(".py", "")
    mid = _meld_id(a, b)
    seed = time.time()

    if mid in _melds:
        return {"status": "already_active", "meld": _melds[mid]}

    ra = _blend_resonance(float(payload.get("resonance_a", 0.6)), float(payload.get("resonance_b", 0.6)))
    emergent = _emergent_property(a, b, seed)
    meld = {
        "id": mid,
        "module_a": a,
        "module_b": b,
        "emergent_property": emergent,
        "resonance": round(ra, 3),
        "created": round(seed, 2),
        "frequency": f"{ra:.2f}Hz",
    }
    _melds[mid] = meld
    return {"status": "melded", "meld": meld}
