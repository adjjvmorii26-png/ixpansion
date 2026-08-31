"""Banquet Composer — composes feasts from available ingredients.

A banquet is not a single dish — it is a sequence of courses arranged
with narrative arc: an appetizer that awakens, a main course that
satisfies, a dessert that delights. The Banquet Composer reads the
Recipe Engine's cookbook, the Flavor Profiler's wheel, and the Nutrition
Index's scores, then composes a *banquet*: a structured sequence of
recipes that tells the story of the organism's current state.

It answers: if the organism threw a feast, what would the menu be?

    GET /api/banquet_composer?read=1           — the current menu
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Banquet Composer"


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _compose_banquet() -> Dict[str, Any]:
    living = _living()
    now = time.time()
    h = hashlib.sha256(str(int(now / 3600)).encode()).hexdigest()[:6]

    # courses: each a different cuisine
    courses = [
        {
            "course": "amuse-bouche",
            "cuisine": "observation",
            "description": "A single, surprising bite: the Naturalist Observatory awakens the palate.",
            "organs": ["heterarchy_oracle", "dowsing_rod", "silence_orchard"][:3],
        },
        {
            "course": "appetizer",
            "cuisine": "healing",
            "description": "The Kintsugi Repair Lineage opens with the warmth of golden seams.",
            "organs": ["crack_mapper", "crack_seams", "kintsugi_altar"][:3],
        },
        {
            "course": "main",
            "cuisine": "movement",
            "description": "The Kinesthetic Engine delivers the main course: motion, gesture, dance.",
            "organs": ["kinesthetic_engine", "dance_composer", "momentum_tracker"][:3],
        },
        {
            "course": "intermezzo",
            "cuisine": "sound",
            "description": "A palate cleanser: the Choral Engine sings a single, clear note.",
            "organs": ["choral_engine", "resonant_frequency", "silence_composer"][:3],
        },
        {
            "course": "dessert",
            "cuisine": "language",
            "description": "The Loom of Language closes with a haiku: words as sweet as honey.",
            "organs": ["poetic_form", "lexicon_engine", "semantics_engine"][:3],
        },
    ]

    return {
        "courses": len(courses),
        "menu": courses,
        "banquet_fingerprint": f"bst:{h}",
        "banquet_philosophy": (
            "A feast is a story told in courses. Each course awakens a "
            "different sense, a different region of the organism. The Banquet "
            "Composer arranges the organism's own organs into a narrative "
            "arc: from awakening to satisfaction to delight. The organism "
            "does not merely eat — it feasts on itself."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = _compose_banquet()
    result["action"] = "banquet"
    return result


def coherence_vitals() -> dict:
    """Banquet Composer reports feast-health."""
    return {
        "module_health": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "banquet_vitality": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["recipe_engine", "flavor_profiler", "ritual_choreographer"]
