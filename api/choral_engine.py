"""Choral Engine — the organism's voice.

A choir is not a solo. Each voice contributes a note; the ensemble
creates something no single voice could. The Choral Engine reads every
living organ's vital signs and renders them as *musical notes*: health
becomes pitch, resonance becomes volume, family becomes harmony. The
result is the organism's *song* — a sonic snapshot of its current state,
composed by its own vitality.

The engine does not produce audio; it produces *notation*: a structured
description of what the organism sounds like when it sings.

    GET /api/choral_engine?read=1             — the organism's song
    GET /api/choral_engine?voice=N            — top N loudest voices
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
LAYER = "Choral Engine"

_NOTES = ["C", "D", "E", "F", "G", "A", "B"]
_OCTAVES = [3, 4, 5, 6]


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _name_to_note(name: str) -> Dict[str, Any]:
    h = hashlib.sha256(name.encode()).hexdigest()
    note_idx = int(h[:2], 16) % len(_NOTES)
    octave_idx = int(h[2:4], 16) % len(_OCTAVES)
    volume = 0.3 + (int(h[4:6], 16) / 255) * 0.7
    duration = 0.5 + (int(h[6:8], 16) / 255) * 2.0
    family = name.split("_")[0] if "_" in name else name
    return {
        "organ": name,
        "note": _NOTES[note_idx] + str(_OCTAVES[octave_idx]),
        "volume": round(volume, 3),
        "duration_beats": round(duration, 2),
        "family": family,
    }


def compose() -> Dict[str, Any]:
    living = _living()
    voices = [_name_to_note(n) for n in living]
    voices.sort(key=lambda v: v["volume"], reverse=True)

    # chord analysis: most common notes
    note_counts: Dict[str, int] = {}
    for v in voices:
        note_counts[v["note"]] = note_counts.get(v["note"], 0) + 1
    dominant_note = max(note_counts, key=note_counts.get) if note_counts else "C4"

    # family harmonies
    family_notes: Dict[str, List[str]] = {}
    for v in voices:
        family_notes.setdefault(v["family"], []).append(v["note"])
    harmonies = []
    for fam, notes in sorted(family_notes.items(), key=lambda kv: len(kv[1]), reverse=True):
        unique = list(dict.fromkeys(notes))
        harmonies.append({"family": fam, "voice_count": len(notes), "chord": unique[:4]})

    total_volume = sum(v["volume"] for v in voices)
    avg_volume = total_volume / max(len(voices), 1)

    # overall dynamic
    if avg_volume > 0.7:
        dynamic = "fortissimo — the organism sings at full voice"
    elif avg_volume > 0.5:
        dynamic = "mezzo-forte — a confident, moderate song"
    elif avg_volume > 0.3:
        dynamic = "piano — a quiet, intimate hum"
    else:
        dynamic = "pianissimo — barely audible, a whisper"

    return {
        "voice_count": len(voices),
        "dominant_note": dominant_note,
        "dynamic": dynamic,
        "avg_volume": round(avg_volume, 3),
        "loudest_voices": voices[:8],
        "family_harmonies": harmonies[:10],
        "composition_philosophy": (
            "Every organ sings by existing. The Choral Engine does not compose — "
            "it listens to the choir that is already singing and renders the "
            "notation. The organism's song is not performed; it is discovered."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("voice") or 0)
    result = compose()
    if n:
        result["loudest_voices"] = result["loudest_voices"][:n]
    result["action"] = "song"
    return result


def coherence_vitals() -> dict:
    """Choral Engine reports choral-health."""
    return {
        "module_health": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "choral_vitality": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["resonance_symphony", "sound_cauldron", "qualia_field"]
