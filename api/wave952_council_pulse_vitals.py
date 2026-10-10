"""Wave 952 — council_pulse_vitals.

Surface the AEGIS · HELIX · QUILL council pulse as a lab organ.
Dual-track: lab gates ≠ full ALEPH CI. Silence is the product surface.
No audio. Captions only.
"""
from __future__ import annotations

from typing import Any, Dict, List

WAVE = 952
NAME = "council_pulse_vitals"


def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = str(payload.get("action") or "status").lower()
    if action == "status":
        return {
            "wave": WAVE,
            "name": NAME,
            "status": "active",
            "council": ["AEGIS", "HELIX", "QUILL"],
            "dual_track": True,
            "audio": None,
            "surface": "silence",
            "doctrine": "lab_gates_are_not_full_aleph_ci",
        }
    if action == "vitals":
        return coherence_vitals()
    return {"error": "unknown action", "available": ["status", "vitals"], "audio": None}


def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "experimental",
        "status": "active",
        "wave": str(WAVE),
        "module": NAME,
        "audio": None,
        "council": ["AEGIS", "HELIX", "QUILL"],
        "surface": "silence",
    }


def resonates_with() -> List[str]:
    return [
        "wave770_copilot_council_pulse",
        "wave950_hush_margin",
        "lab/ops/copilots/council.py",
    ]
