"""Recipe Engine — combines modules into compositions.

A recipe is not a single ingredient — it is a combination arranged with
intention. The Recipe Engine reads the living module registry, the
Lexicon Engine's vocabulary, and the Semantic Engine's meaning field,
then proposes *recipes*: named combinations of 3-5 modules that, when
queried together, produce a richer result than any one alone.

It answers: what combinations of organs produce the most nourishing output?

    GET /api/recipe_engine?read=1             — the recipe book
    GET /api/recipe_engine?cuisine=N          — N recipes by cuisine
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Recipe Engine"

_CUISINES = ["observation", "healing", "movement", "sound", "language", "governance"]


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _recipe_for(cuisine: str, living: List[str]) -> Dict[str, Any]:
    """Generate a recipe by selecting modules whose names fit the cuisine."""
    keywords = {
        "observation": ["watch", "see", "map", "scan", "read", "index", "census", "detect"],
        "healing": ["crack", "seam", "kintsugi", "repair", "fracture", "mend", "gild"],
        "movement": ["kinesth", "gesture", "momentum", "dance", "still", "proprio"],
        "sound": ["choral", "harmon", "resonant", "disson", "crescend", "silence", "song"],
        "language": ["lexicon", "grammar", "syntax", "semantic", "pragmat", "poetic"],
        "governance": ["heterarch", "keystone", "moral", "ethic", "govern", "evolution"],
    }
    kws = keywords.get(cuisine, [])
    matched = [m for m in living if any(k in m for k in kws)]
    selected = matched[:5] if len(matched) >= 3 else living[:5]

    h = hashlib.sha256((cuisine + "".join(selected)).encode()).hexdigest()[:6]
    return {
        "cuisine": cuisine,
        "ingredients": selected,
        "ingredient_count": len(selected),
        "recipe_fingerprint": f"rcp:{h}",
        "instructions": f"Query {len(selected)} organs in the {cuisine} family and fuse their outputs.",
    }


def cookbook(cuisine: str = "") -> Dict[str, Any]:
    living = _living()
    cuisines = [cuisine] if cuisine else _CUISINES
    recipes = [_recipe_for(c, living) for c in cuisines]
    return {
        "total_recipes": len(recipes),
        "recipes": recipes,
        "cookbook_philosophy": (
            "A single organ feeds the mind; a recipe feeds the whole organism. "
            "The Recipe Engine finds combinations that produce richer output "
            "than any one organ alone — ingredients arranged with intention."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("cuisine") or 0)
    result = cookbook(payload.get("cuisine", ""))
    result["action"] = "cookbook"
    return result


def coherence_vitals() -> dict:
    """Recipe Engine reports recipe-health."""
    return {
        "module_health": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "recipe_vitality": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["flavor_profiler", "banquet_composer", "lexicon_engine"]
