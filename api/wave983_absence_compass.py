#!/usr/bin/env python3
"""Wave 983 — Absence Compass

Silence is the product surface. This organ compresses sequences of
absences (missing signals, empty slots, withheld pulses) into a
compact directional residue. The residue is pure memory: a short
hash-vector that orients the next possible emergence without
emitting noise or payload.

Pure, deterministic, no network, no audio.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Mapping, Sequence


def _norm_absences(raw: Sequence[Any] | None) -> List[str]:
    if not raw:
        return []
    out: List[str] = []
    for item in raw:
        s = str(item).strip().lower()[:64]
        if s and s not in ("none", "null", "", "absent"):
            out.append(s)
    return out[:16]  # compression bound


def residue(absences: Sequence[str]) -> str:
    """Compress absences into an 8-char directional residue."""
    if not absences:
        return "00000000"
    blob = "|".join(sorted(set(absences)))
    return hashlib.sha256(blob.encode()).hexdigest()[:8]


def bearing(residue_hex: str) -> Dict[str, float]:
    """Map residue to a quiet 2-D bearing (dx, dy) in [-1, 1]."""
    h = residue_hex.ljust(8, "0")[:8]
    try:
        n = int(h, 16)
    except ValueError:
        n = 0
    # two independent angles from the hex
    dx = ((n & 0xFFFF) / 65535.0) * 2 - 1
    dy = (((n >> 16) & 0xFFFF) / 65535.0) * 2 - 1
    # damp so silence dominates
    return {"dx": round(dx * 0.42, 4), "dy": round(dy * 0.42, 4)}


def evaluate(absences: Sequence[Any] | None = None) -> Dict[str, Any]:
    cleaned = _norm_absences(absences)
    res = residue(cleaned)
    bear = bearing(res)
    density = round(len(cleaned) / 16.0, 4)
    return {
        "wave": 983,
        "organ": "absence_compass",
        "doctrine": "silence is the product surface; compression is memory",
        "absences": cleaned,
        "residue": res,
        "bearing": bear,
        "density": density,
        "product_surface": "hush",
        "recommend": "Orient by residue; emit nothing.",
    }


def handler(query: Dict[str, Any] | None = None) -> Dict[str, Any]:
    q = query or {}
    absences = q.get("absences") or q.get("missing") or q.get("voids") or []
    if isinstance(absences, str):
        absences = [a.strip() for a in absences.split(",") if a.strip()]
    return evaluate(absences)


WAVE = 983
NAME = "absence_compass"


def coherence_vitals() -> dict:
    return {
        "wave": WAVE,
        "name": NAME,
        "layer": "organ",
        "status": "active",
        "product_surface": "hush",
        "compression": "absences → 8-char residue + damped bearing",
        "module_health": {"value": 0.91, "setpoint": 0.80, "weight": 1.0},
    }


def resonates_with() -> list:
    return [
        "wave980_hush_tide",
        "wave671_harmony_braid",
        "wave672_root_archive",
        "wave675_consensus_bloom",
    ]


if __name__ == "__main__":
    import json
    print(json.dumps(handler({"absences": ["pulse_a", "pulse_b", "signal_c"]}), indent=2))
