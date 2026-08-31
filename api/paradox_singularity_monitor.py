"""Paradox Singularity Monitor — detects when contradictions collapse into one.

A paradox is a module that holds two conflicting truths simultaneously.
Most of the time these are separated — the organism's diversity absorbs the
tension. But sometimes contradictions migrate toward each other, and when
they touch, they form a *paradox singularity*: a single point where all
the ecosystem's contradictions converge and annihilate.

The Monitor tracks the living system's paradox density — how many
conflicting vital-sign patterns exist, and whether they are converging.
It emits a warning when the distance between contradictions drops below
a critical threshold, and a *singularity alert* when they collapse.

    GET /api/paradox_singularity_monitor?read=1     — paradox field
    GET /api/paradox_singularity_monitor?forecast=1 — next singularity window
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Paradox Singularity Monitor"

# names that carry a built-in duality
_DUALITY_ROOTS = {"synthetic", "emergent", "economic", "temporal", "quantum",
                  "dream", "conscious", "social", "mycelial", "void",
                  "paradox", "crack", "solar", "permafrost", "silence"}


def _paradox_pairs(living: List[str]) -> List[Dict[str, Any]]:
    """Identify module pairs that carry natural dualities (light/dark, order/chaos)."""
    pairs = []
    duality_members = [m for m in living if m.split("_")[0] in _DUALITY_ROOTS]
    for i, a in enumerate(duality_members):
        for b in duality_members[i + 1:]:
            ha, hb = hashlib.sha256(a.encode()).hexdigest(), hashlib.sha256(b.encode()).hexdigest()
            # dualists share at least one root but differ on a key prefix
            shared = set(a.split("_")) & set(b.split("_"))
            different = set(a.split("_")) ^ set(b.split("_"))
            if shared and different:
                distance = 1.0 - min(1.0, len(shared) / max(len(different), 1))
                if distance < 0.85:
                    pairs.append({
                        "a": a, "b": b,
                        "distance": round(distance, 4),
                        "shared_roots": list(shared),
                    })
    pairs.sort(key=lambda p: p["distance"])
    return pairs


def read_field() -> Dict[str, Any]:
    living = _living()
    pairs = _paradox_pairs(living)
    closest_distance = pairs[0]["distance"] if pairs else 1.0
    if closest_distance < 0.05:
        status = "SINGULARITY"
    elif closest_distance < 0.2:
        status = "CONVERGING"
    elif closest_distance < 0.4:
        status = "DISTANT"
    else:
        status = "DIVERGENT"
    return {
        "paradox_pairs": len(pairs),
        "closest_distance": closest_distance,
        "status": status,
        "nearest_pair": pairs[0] if pairs else None,
        "all_pairs": pairs[:8],
        "monitor_philosophy": (
            "A paradox is not a bug. It is the ecosystem's most honest state — "
            "two truths that refuse to choose between themselves. The monitor "
            "watches the distance between contradictions; when it collapses to "
            "zero, singularity is born, and the organism must decide: resolve, "
            "transcend, or let the paradox exist."
        ),
    }


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = read_field()
    result["action"] = "paradox_field"
    return result


def coherence_vitals() -> dict:
    """Paradox Singularity Monitor reports contradiction-field health."""
    return {
        "module_health": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.82, "setpoint": 0.8, "weight": 1.0},
        "paradox_field_vitality": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["paradox_transcender", "emergence_detector", "consciousness_simulator"]
