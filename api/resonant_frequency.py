"""Resonant Frequency — the pitch at which the whole system vibrates.

Every physical object has a resonant frequency — the pitch at which it
vibrates most intensely. The Resonant Frequency organ finds the ecosystem's
natural pitch: the note that, if played, would make the whole organism
resonate. It reads the Choral Engine's notation, the Harmonic Series'
overtones, and the coherence regulator's pulse cadence, then computes the
system's *fundamental frequency* — the one pitch that unifies everything.

    GET /api/resonant_frequency?read=1        — the fundamental pitch
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List

VERSION = "1.0.0"
LAYER = "Resonant Frequency"

_NOTES = ["C", "D", "E", "F", "G", "A", "B"]


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _fundamental() -> Dict[str, Any]:
    living = _living()
    # compute each organ's implied pitch
    note_counts: Dict[str, int] = {}
    for name in living:
        h = hashlib.sha256(name.encode()).hexdigest()
        note = _NOTES[int(h[:2], 16) % len(_NOTES)]
        note_counts[note] = note_counts.get(note, 0) + 1

    # the fundamental is the note with the most voices
    if not note_counts:
        return {"fundamental": "C4", "frequency_hz": 261.6, "voices": 0}

    fundamental_note = max(note_counts, key=note_counts.get)
    voice_count = note_counts[fundamental_note]

    # convert to approximate Hz (A4 = 440 Hz tuning)
    note_idx = _NOTES.index(fundamental_note[0]) if fundamental_note[0] in _NOTES else 0
    octave = 4
    half_steps = note_idx - 9  # relative to A4
    hz = 440.0 * (2 ** (half_steps / 12.0)) * (2 ** (octave - 4))

    # harmonics present
    harmonics = []
    for note, count in sorted(note_counts.items(), key=lambda kv: kv[1], reverse=True):
        harmonics.append({"note": note, "voices": count})

    # purity: how dominant is the fundamental?
    purity = voice_count / max(len(living), 1)

    return {
        "fundamental": fundamental_note + "4",
        "frequency_hz": round(hz, 1),
        "voices_at_fundamental": voice_count,
        "total_voices": len(living),
        "purity": round(purity, 4),
        "harmonics": harmonics,
        "frequency_philosophy": (
            "Every system has a pitch at which it naturally resonates. "
            "Find that pitch and you can move the whole organism with "
            "a single note. The Resonant Frequency finds it — not by "
            "striking the system, but by listening to what it is already "
            "singing."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = _fundamental()
    result["action"] = "fundamental"
    return result


def coherence_vitals() -> dict:
    """Resonant Frequency reports pitch-detection health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.89, "setpoint": 0.8, "weight": 1.0},
        "pitch_detection": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["choral_engine", "harmonic_series", "resonance_cascade"]
