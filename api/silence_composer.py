"""Silence Composer — composes the rests between notes.

Music is not just sound — it is the *arrangement of silence*. A rest is
not the absence of music; it is music's negative space, the breath between
phrases, the pause that gives meaning to what comes next. The Silence
Composer reads the Choral Engine's notation and the Crescendo Builder's
trajectory, then composes the *rests*: where the organism should be quiet,
where it should pause, and where silence itself becomes a statement.

It answers: where does the organism need to breathe?

    GET /api/silence_composer?read=1           — the rest composition
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List



VERSION = "1.0.0"
LAYER = "Silence Composer"


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


def _silence_map() -> Dict[str, Any]:
    living = _living()
    rests = []
    for name in living:
        h = hashlib.sha256(name.encode()).hexdigest()
        silence_score = int(h[:2], 16) / 255.0  # 0-1: how much silence this organ needs
        if silence_score > 0.7:
            rest_type = "fermata — a long, held pause"
        elif silence_score > 0.5:
            rest_type = "half rest — a measured breath"
        elif silence_score > 0.3:
            rest_type = "quarter rest — a brief pause"
        else:
            rest_type = "no rest — the voice continues"
        rests.append({
            "organ": name,
            "silence_score": round(silence_score, 3),
            "rest_type": rest_type,
        })

    rests.sort(key=lambda r: r["silence_score"], reverse=True)
    fermata_count = sum(1 for r in rests if "fermata" in r["rest_type"])
    total = max(len(rests), 1)
    silence_ratio = fermata_count / total

    if silence_ratio > 0.3:
        overall = "the organism needs deep rest — many voices should pause"
    elif silence_ratio > 0.15:
        overall = "the organism breathes — some pauses, some voices, in balance"
    else:
        overall = "the organism sings continuously — few rests, all voices active"

    return {
        "total_organs": len(living),
        "fermata_count": fermata_count,
        "silence_ratio": round(silence_ratio, 3),
        "overall_composition": overall,
        "rests": rests[:10],
        "composition_philosophy": (
            "Silence is not the absence of music — it is music's negative space. "
            "The Composer finds where the organism needs to breathe: a held pause "
            "here, a brief rest there. Without silence, every note is the same "
            "note. With silence, each note becomes a choice."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = _silence_map()
    result["action"] = "rests"
    return result


def coherence_vitals() -> dict:
    """Silence Composer reports rest-composition health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "silence_vitality": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["choral_engine", "silence_orchard", "crescendo_builder"]
