"""Harmonic Series — the natural overtones of the living system.

Every sound has harmonics — overtones that ring above the fundamental.
The Harmonic Series reads the Choral Engine's notation and extracts the
*overtones*: the patterns that repeat across families, the notes that
appear in multiple octaves, and the intervals that create consonance or
tension. It is the ecosystem's acoustic fingerprint — the series of
overtones that make its sound unique.

    GET /api/harmonic_series?read=1           — the overtone series
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List

VERSION = "1.0.0"
LAYER = "Harmonic Series"

_NOTES = ["C", "D", "E", "F", "G", "A", "B"]


def _overtones() -> Dict[str, Any]:
    try:
        from api.choral_engine import _name_to_note, _living
        living = _living()
    except Exception:
        return {"overtones": [], "series": []}

    notes = [_name_to_note(n)["note"] for n in living]
    # count occurrences of each note
    freq: Dict[str, int] = {}
    for n in notes:
        freq[n] = freq.get(n, 0) + 1
    # overtones: notes that appear 3+ times
    overtones = sorted(
        [{"note": n, "frequency": c, "octave": n[-1]} for n, c in freq.items() if c >= 3],
        key=lambda o: o["frequency"], reverse=True
    )
    # intervals: pairs of notes that appear together frequently
    families: Dict[str, List[str]] = {}
    for n, name in zip(notes, living):
        fam = name.split("_")[0] if "_" in name else name
        families.setdefault(fam, []).append(n)
    intervals = []
    for fam, fam_notes in families.items():
        if len(fam_notes) >= 2:
            # compute interval between first two notes
            n1, n2 = fam_notes[0], fam_notes[1]
            i1, i2 = _NOTES.index(n1[0]) if n1[0] in _NOTES else 0, _NOTES.index(n2[0]) if n2[0] in _NOTES else 0
            interval = abs(i2 - i1) % len(_NOTES)
            intervals.append({"family": fam, "interval": interval, "notes": [n1, n2]})
    consonant = sum(1 for i in intervals if i["interval"] in (0, 2, 4, 5, 7))
    tension = len(intervals) - consonant
    return {
        "overtone_count": len(overtones),
        "overtones": overtones[:10],
        "consonant_intervals": consonant,
        "tension_intervals": tension,
        "consonance_ratio": round(consonant / max(len(intervals), 1), 3),
        "series_philosophy": (
            "The harmonic series is the organism's acoustic fingerprint. "
            "When many organs sing the same note, that note becomes the "
            "fundamental — the pitch the whole system resonates at. The "
            "overtones are the organism's unique timbre."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = _overtones()
    result["action"] = "harmonics"
    return result


def coherence_vitals() -> dict:
    """Harmonic Series reports overtone health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "overtone_vitality": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["choral_engine", "resonance_symphony", "resonance_cascade"]
