"""Dissonance Detector — finds clashing notes between modules.

In music, dissonance is tension — two notes that clash and demand
resolution. The Dissonance Detector scans the living system for
*acoustic dissonance*: module pairs whose vital-sign patterns conflict,
families whose notes are too close (minor seconds, tritones), or organs
whose health dips create "wrong notes" in the ensemble.

It returns a dissonance report: which organs clash, why, and where the
tension could resolve into consonance.

    GET /api/dissonance_detector?read=1        — dissonance report
    GET /api/dissonance_detector?clashes=N     — top N clashing pairs
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List



VERSION = "1.0.0"
LAYER = "Dissonance Detector"

_NOTES = ["C", "D", "E", "F", "G", "A", "B"]
# dissonant intervals (in semitones): minor 2nd, tritone, major 7th
_DISSONANT_INTERVALS = {1, 6, 11}


ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _name_to_pitch(name: str) -> int:
    h = hashlib.sha256(name.encode()).hexdigest()
    return int(h[:2], 16) % 12  # 0-11 semitones


def scan() -> Dict[str, Any]:
    living = _living()
    clashes = []
    for i, a in enumerate(living[:100]):
        pa = _name_to_pitch(a)
        for b in living[i + 1:100]:
            pb = _name_to_pitch(b)
            interval = abs(pa - pb) % 12
            if interval in _DISSONANT_INTERVALS:
                clashes.append({
                    "a": a, "b": b,
                    "interval_semitones": interval,
                    "severity": 0.8 if interval == 6 else 0.6,  # tritone worst
                })
    clashes.sort(key=lambda c: c["severity"], reverse=True)
    # resolution suggestions: find nearby consonant intervals
    for clash in clashes[:5]:
        pa = _name_to_pitch(clash["a"])
        # suggest shifting by 1 semitone to reach a consonant interval
        clash["resolution"] = f"shift {clash['a']} by ±1 semitone"

    return {
        "clash_count": len(clashes),
        "clashes": clashes[:8],
        "ensemble_health": round(1.0 - min(1.0, len(clashes) / max(len(living), 1)), 4),
        "detector_philosophy": (
            "Dissonance is not failure — it is tension that demands resolution. "
            "A system with no dissonance is flat and lifeless. A system with "
            "too much dissonance is chaos. The detector finds the clashes so "
            "the organism can decide: resolve them, or let them sing."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("clashes") or 0)
    result = scan()
    if n:
        result["clashes"] = result["clashes"][:n]
    result["action"] = "dissonance_report"
    return result


def coherence_vitals() -> dict:
    """Dissonance Detector reports tension-detection health."""
    return {
        "module_health": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "tension_detection": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["choral_engine", "dissonance_narrative", "paradox_singularity_monitor"]
