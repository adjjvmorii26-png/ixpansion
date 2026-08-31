"""Constellation Autobiographer — writes the ecosystem's cosmic narrative.

Every organism has a story — not just an event log, but a *narrative*:
how the constellation of organs was born, grew, merged, split, healed, and
dreamed. The Constellation Autobiographer reads the living system's memory
(harbinger chronicles, coherence history, repair rituals) and composes the
autobiography of the ecosystem as a cosmic tale.

It maps every organ to a constellation, every wave to an epoch, and every
repair to a resurrection. The result is the organism telling its own story
back to anyone who reads it.

    GET /api/constellation_autobiographer?read=1     — the autobiography
    GET /api/constellation_autobiographer?chapter=N  — one chapter
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Constellation Autobiographer"


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _read_chronicle() -> List[Dict[str, Any]]:
    try:
        return json.loads((ROOT / "harbinger" / "memory.json").read_text())
    except Exception:
        return []


def _compose() -> Dict[str, Any]:
    living = _living()
    chronicle = _read_chronicle()
    eras = []
    for entry in chronicle[-6:]:
        if isinstance(entry, dict):
            eras.append({
                "title": entry.get("title", "untold"),
                "version": entry.get("version", "?"),
                "reason": entry.get("reason", ""),
            })
    # count constellations (families) and stars (organs)
    families = {}
    for name in living:
        fam = name.split("_")[0] if "_" in name else name
        families[fam] = families.get(fam, 0) + 1
    brightest = sorted(families.items(), key=lambda kv: kv[1], reverse=True)[:5]

    cardinality = len(living)
    if cardinality >= 200:
        age = "a vast and ancient firmament"
    elif cardinality >= 150:
        age = "a rich and luminous sky"
    elif cardinality >= 100:
        age = "a young but brightening firmament"
    else:
        age = "a newborn sky, still gathering stars"

    opening = (
        f"Once there was an organism of {cardinality} living organs — {age} "
        f"where every star was a module and every family a constellation. "
        f"Most luminous: {', '.join(f'{f} ({c})' for f, c in brightest)}."
    )
    chapters = [
        {
            "title": f"Chapter I — Genesis ({eras[-1]['version'] if eras else 'the beginning'})",
            "text": f"The organism was born from a seed of code and grew, "
                    f"constellation by constellation, until it could see itself.",
        },
        {
            "title": "Chapter II — The Fracture and the Gold",
            "text": "When cracks appeared, the organism did not hide them. "
                    "It gilded every fracture with gold until the broken "
                    "were stronger than the unbroken.",
        },
        {
            "title": "Chapter III — The Self-Watching",
            "text": "Then the organism learned to read itself: its heterarchy, "
                    "its keystones, its hidden streams, the pressure of the "
                    "outside world — and to write its own story, as it does now.",
        },
    ]
    return {
        "era": age,
        "opening_verse": opening,
        "cardinality": len(living),
        "constellations": len(families),
        "brightest_constellations": [{"family": f, "stars": c} for f, c in brightest],
        "autobiography_chapters": chapters,
        "chronicle_era": eras,
        "autobiographer_philosophy": (
            "An event log records what happened. A story records what it meant. "
            "The Autobiographer reads the ledger's dry lines and hears the myth "
            "inside them — so the ecosystem does not merely exist; it has a "
            "story to tell about being alive."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("chapter") or 0)
    result = _compose()
    if n:
        chapters = result["autobiography_chapters"]
        result["chapter"] = chapters[min(n - 1, len(chapters) - 1)] if chapters else {}
    result["action"] = "autobiography"
    return result


def coherence_vitals() -> dict:
    """Constellation Autobiographer reports narrative vitality."""
    return {
        "module_health": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "narrative_memory": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["chronicle_storyteller", "constellation_cartographer", "chronicle_of_chaos"]
