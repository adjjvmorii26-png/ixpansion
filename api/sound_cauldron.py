"""Sound Cauldron — brews any text into a procedural soundscape.

Turns words into sound: each token becomes a note, word length sets the
note duration, letter frequency picks the pitch, and punctuation sets the
rhythm. The result is a deterministic musical rendering of any input —
a module name, a prophecy, a query.

Usage:
  GET  /api/sound_cauldron?text=consciousness
  POST /api/sound_cauldron {"text": "The frontier dreams in code"}
  GET  /api/sound_cauldron?text=garden&scale=pentatonic
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import re
from typing import Any, Dict, List

# Pentatonic scale (major): C D E G A
PENTATONIC = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21]
# Chromatic octave offset
CHROMATIC = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
SCALES = {
    "pentatonic": PENTATONIC,
    "chromatic": CHROMATIC,
    "major": [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19],
    "minor": [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19],
}


def _hash_int(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)


def _note_from_char(char: str) -> int:
    """Map a character to a scale degree."""
    return ord(char.lower()) - ord("a") if char.isalpha() else 0


def _freq_from_scale_degree(degree: int, base: float = 220.0) -> float:
    """Convert a scale degree to a frequency in Hz (A3 base)."""
    return base * (2 ** (degree / 12))


def _rhythm(token: str) -> float:
    """Token length sets the rhythmic duration (shorter = snappier)."""
    return max(0.3, min(2.0, len(token) * 0.18))


def _tempo(text: str) -> int:
    """Word count + punctuation sets the tempo (BPM)."""
    words = re.findall(r"[a-z]+", text.lower())
    punctuation = sum(1 for c in text if c in ".,!?;:")
    base = 60 + len(words) * 4
    return min(180, base + punctuation * 10)


def _timbre(text: str) -> str:
    """Text sentiment-ish heuristic maps to a timbre."""
    h = _hash_int(text)
    timbres = ["glass", "reed", "string", "bell", "breath", "metal", "water", "light"]
    return timbres[h % len(timbres)]


def _register(text: str) -> str:
    """Overall dynamic/register."""
    avg_len = sum(len(w) for w in re.findall(r"[a-z]+", text.lower())) / max(len(re.findall(r"[a-z]+", text.lower())), 1)
    if avg_len < 4:
        return "whisper"
    if avg_len < 7:
        return "conversational"
    if avg_len < 10:
        return "annunciated"
    return "incantatory"


def brew(text: str, scale: str = "pentatonic", key_offset: int = 0,
         max_notes: int = 60) -> Dict[str, Any]:
    """Brew text into a complete soundscape."""
    words = re.findall(r"[a-zA-Z]+", text)
    punctuation = re.findall(r"[.,!?;:]", text)
    scale_degrees = SCALES.get(scale, PENTATONIC)

    # Build the note sequence
    notes = []
    cumulative_time = 0.0
    for i, word in enumerate(words):
        h = _hash_int(word + str(i))
        # Note: base on first letter mapping into the scale
        degree_index = _note_from_char(word[0]) % len(scale_degrees)
        degree = scale_degrees[degree_index] + key_offset
        # octave lift for longer words
        while degree > 24:
            degree -= 12
        freq = _freq_from_scale_degree(degree)

        notes.append({
            "index": i,
            "token": word,
            "frequency_hz": round(freq, 2),
            "duration_s": round(_rhythm(word), 2),
            "start_s": round(cumulative_time, 2),
            "velocity": round(0.4 + 0.6 * (h / (2**32)), 2),  # loudness
        })
        cumulative_time += _rhythm(word)
        if len(notes) >= max_notes:
            break

    # Add rests (breaths) at punctuation
    total_duration = cumulative_time + len(punctuation) * 0.4

    first_freq = notes[0]["frequency_hz"] if notes else 220.0
    melodic_range = max(n["frequency_hz"] for n in notes) - min(n["frequency_hz"] for n in notes) if notes else 0

    return {
        "text": text,
        "scale": scale,
        "key_offset": key_offset,
        "tempo_bpm": _tempo(text),
        "timbre": _timbre(text),
        "register": _register(text),
        "notes_count": len(notes),
        "notes": notes,
        "canvas": {
            "total_duration_s": round(total_duration, 2),
            "melodic_range_hz": round(melodic_range, 2),
            "first_frequency_hz": round(first_freq, 2),
            "final_frequency_hz": round(notes[-1]["frequency_hz"], 2) if notes else first_freq,
        },
        "scoresheet": (
            f"{_tempo(text)} BPM, {_timbre(text)} timbre, "
            f"{_register(text)} register, {len(notes)} notes over "
            f"{round(total_duration, 1)} seconds."
        ),
        "philosophy": "Every word is a note waiting to be played. The frontier does not just read its concepts — it hears them.",
    }


def coherence_vitals() -> dict:
    """Sound Cauldron reports harmonic balance."""
    return {"harmonic_balance": 0.9,
            "module_health": 0.9,
            "resonance": {"value": 0.83, "setpoint": 0.8, "weight": 1.0}}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    text = payload.get("text", payload.get("query", "the frontier dreams"))
    scale = payload.get("scale", "pentatonic")
    key_offset = int(payload.get("key", 0))
    max_notes = int(payload.get("notes", 60))

    if scale not in SCALES:
        scale = "pentatonic"

    result = brew(text, scale, key_offset, max_notes)
    result["action"] = "brew"
    result["scales_available"] = list(SCALES.keys())
    return result


def resonates_with() -> list:
    """Declared kinships — the composer brews music from every
    domain, so it sings through synesthesia (sensory translation),
    draws worlds from reality_weaver, and dreams with dream_sequencer."""
    return ["synesthesia", "reality_weaver", "dream_sequencer"]

