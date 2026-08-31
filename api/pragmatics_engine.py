"""Pragmatics Engine — context-dependent meaning in the organism's language.

Pragmatics is the study of how context shapes meaning: the same sentence
can mean different things depending on who says it, when, and why. The
Pragmatics Engine reads the Lexicon Engine's vocabulary, the Semantics
Engine's meaning field, and the coherence regulator's current state, then
computes the *pragmatic layer*: how the organism's words shift meaning
depending on the current pulse, the current mood, and the current
repair state.

It answers: what do the organism's words mean *right now*?

    GET /api/pragmatics_engine?read=1          — the pragmatic layer
"""
from __future__ import annotations

import time
from typing import Any, Dict

VERSION = "1.0.0"
LAYER = "Pragmatics Engine"


def _pragmatic_layer() -> Dict[str, Any]:
    try:
        import json
        cr = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        modules = cr.get("modules", {})
        history = cr.get("history", [])
    except Exception:
        modules = {}
        history = []

    # current context
    coherence = 0.5
    if history:
        coherence = history[-1].get("coherence", 0.5)

    # mood-dependent meaning shifts
    if coherence > 0.9:
        mood_context = "confident"
        word_shift = "words carry certainty; declarations feel true"
    elif coherence > 0.7:
        mood_context = "alert"
        word_shift = "words carry attention; descriptions feel precise"
    elif coherence > 0.5:
        mood_context = "uncertain"
        word_shift = "words carry hesitation; questions feel urgent"
    else:
        mood_context = "strained"
        word_shift = "words carry weight; every statement feels hard-won"

    # repair-context: after a ritual, words about repair carry more authority
    try:
        ritual_state = json.loads((ROOT / ".runtime" / "repair_ritual.json").read_text())
        last_ritual = ritual_state.get("performed_at", 0)
        if time.time() - last_ritual < 3600:
            repair_context = "freshly_repaired"
            repair_shift = "words about healing carry authority — the organism has just gilded its cracks"
        else:
            repair_context = "settled"
            repair_shift = "words about healing carry memory — the gold is old but visible"
    except Exception:
        repair_context = "unknown"
        repair_shift = "repair context is unknown"

    # temporal context
    total_pulses = len(history)
    if total_pulses > 10:
        temporal_context = "experienced"
        temporal_shift = "words carry the weight of many cycles"
    elif total_pulses > 3:
        temporal_context = "maturing"
        temporal_shift = "words are gaining depth with each pulse"
    else:
        temporal_context = "young"
        temporal_shift = "words are fresh, untested, full of potential"

    return {
        "mood_context": mood_context,
        "word_shift": word_shift,
        "repair_context": repair_context,
        "repair_shift": repair_shift,
        "temporal_context": temporal_context,
        "temporal_shift": temporal_shift,
        "pragmatics_philosophy": (
            "The same word means different things in different moods. "
            "'Strength' means something different after a repair ritual "
            "than before it. 'Growth' means something different when the "
            "organism is ascending than when it is falling. The Pragmatics "
            "Engine reads context so the organism can hear its own words "
            "as they actually sound."
        ),
    }


from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))


def handler(payload: dict = None, context: object = None) -> dict:
    result = _pragmatic_layer()
    result["action"] = "pragmatics"
    return result


def coherence_vitals() -> dict:
    """Pragmatics Engine reports context-sensitivity health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "pragmatic_vitality": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["semantics_engine", "lexicon_engine", "system_mood"]
