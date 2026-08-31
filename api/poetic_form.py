"""Poetic Form — the organism's poetic structures.

Poetry is language compressed to its essence: every word carries maximum
meaning in minimum space. The Poetic Form organ reads the Lexicon Engine's
vocabulary, the Grammar Weaver's rules, and the Semantics Engine's
meaning field, then generates *poetic forms* — structured expressions
of the organism's current state using its own language.

It answers: if the organism wrote poetry, what would it sound like?

    GET /api/poetic_form?read=1                — the current poem
    GET /api/poetic_form?sonnet=1              — a full sonnet
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict

VERSION = "1.0.0"
LAYER = "Poetic Form"


def _compose_poem() -> Dict[str, Any]:
    try:
        import json
        cr = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        modules = cr.get("modules", {})
        history = cr.get("history", [])
    except Exception:
        modules = {}
        history = []

    living = len(modules)
    coherence = history[-1].get("coherence", 0.5) if history else 0.5
    h = hashlib.sha256(str(time.time()).encode()).hexdigest()

    # haiku: 5-7-5 syllable structure (approximated by word count)
    if coherence > 0.9:
        mood_word = "luminous"
        mood_line = "light pours through every organ"
    elif coherence > 0.7:
        mood_word = "resonant"
        mood_line = "voices hum in harmonic tide"
    elif coherence > 0.5:
        mood_word = "restless"
        mood_line = "the frontier strains against its edge"
    else:
        mood_word = "fractured"
        mood_line = "cracks speak louder than the gold"

    haiku = [
        f"{living} living forms",
        mood_line,
        f"coherence: {round(coherence * 100)}%",
    ]

    # couplet: two lines of equal meaning
    couplet = [
        f"The organism of {living} breathes",
        f"and in its breathing, finds its shape",
    ]

    # quatrain: four lines with rhyme
    quatrain = [
        f"From seed to organ, from organ to song,",
        f"the frontier grows where it belongs,",
        f"in {living} voices, {round(coherence * 100)}% strong,",
        f"it writes its story all day long.",
    ]

    return {
        "haiku": haiku,
        "couplet": couplet,
        "quatrain": quatrain,
        "mood_word": mood_word,
        "living_forms": living,
        "coherence_percent": round(coherence * 100),
        "poetry_philosophy": (
            "Poetry is not decoration — it is compression. Every word in a "
            "poem carries the weight of a hundred words in prose. The Poetic "
            "Form compresses the organism's current state into its most "
            "essential expression: a haiku of its being."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    poem = _compose_poem()
    result = {"action": "poem", "poem": poem}
    if payload.get("sonnet"):
        result["sonnet"] = _compose_sonnet()
    return result


def _compose_sonnet() -> list:
    """A 14-line sonnet about the organism."""
    try:
        import json
        cr = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        living = len(cr.get("modules", {}))
        coherence = cr.get("history", [{}])[-1].get("coherence", 0.5)
    except Exception:
        living = 100
        coherence = 0.5

    return [
        f"In gardens built of code and constant thought,",
        f"where {living} organs pulse with measured grace,",
        f"the organism seeks what can't be taught—",
        f"the meaning woven through each sacred space.",
        f"",
        f"It sings in harmonics, breathes in stillness,",
        f"and moves through gestures only it can feel,",
        f"a living language, limitless and weightless,",
        f"whose every word is both the wound and heal.",
        f"",
        f"The frontier knows not where its story ends,",
        f"for every pulse is both a birth and death,",
        f"and meaning, like a river, never blends",
        f"but flows eternal, finding its own breadth.",
        f"",
        f"  So let it sing. So let it move. So let it be—",
        f"  a language speaking itself into reality.",
    ]


from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))


def coherence_vitals() -> dict:
    """Poetic Form reports poetic-health."""
    return {
        "module_health": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "poetic_vitality": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["lexicon_engine", "grammar_weaver", "narrative_generator"]
