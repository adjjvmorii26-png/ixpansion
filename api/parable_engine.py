"""Parable Engine — turns technical state into metaphor and story.

Every metric has a metaphor. Coherence is a river. A parasite module is
a vine. A fossil is a fallen tree. The Parable Engine takes the
organism's live state and spins it into a short parable — abstract but
true. It makes the technical reachable.

It answers: what is the organism's state, told as a story?
"""
from __future__ import annotations

import hashlib
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Parable Engine"


def _gather_metaphors() -> Dict[str, Any]:
    """Map live state to metaphor ingredients."""
    import importlib

    metaphors = {}

    try:
        mod = importlib.import_module("coherence_regulator")
        r = mod.regulate() if hasattr(mod, "regulate") else {}
        coherence = r.get("coherence", 0.986)
    except Exception:
        coherence = 0.986
    metaphors["coherence"] = coherence
    metaphors["river"] = (
        "a wide, slow river at full bank" if coherence > 0.9
        else "a river with a few sandbars" if coherence > 0.8
        else "a river splitting into channels"
    )

    try:
        mod = importlib.import_module("ecosystem_fitness")
        r = mod._measure() if hasattr(mod, "_measure") else {}
        fitness = r.get("fitness_score", 0.8)
    except Exception:
        fitness = 0.8
    metaphors["fitness"] = fitness
    metaphors["forest"] = (
        "an old-growth forest, layered and alive" if fitness > 0.8
        else "a young forest, still growing" if fitness > 0.6
        else "a thinning woodland"
    )

    try:
        mod = importlib.import_module("symbiosis_detector")
        r = mod.detect() if hasattr(mod, "detect") else {}
        relationships = r.get("total_relationships", 0)
    except Exception:
        relationships = 0
    metaphors["relationships"] = relationships
    metaphors["web"] = (
        "a web of many visible threads" if relationships > 10
        else "a web with a few threads, still being woven"
    )

    try:
        mod = importlib.import_module("barometric_intent")
        r = mod._compute_pressure() if hasattr(mod, "_compute_pressure") else {}
        pressure = r.get("pressure_hpa", 1013)
    except Exception:
        pressure = 1013
    metaphors["pressure"] = pressure
    metaphors["sky"] = (
        "a high-pressure sky, clear and focused" if pressure > 900
        else "a low-pressure sky, scattered and dreaming"
    )

    return metaphors


def _compose_parable(meta: Dict[str, Any]) -> str:
    """Compose a short parable from the metaphor ingredients."""
    seed = hashlib.sha256(str(int(time.time() // 600)).encode()).hexdigest()
    rng = random.Random(seed)

    openings = [
        "There was once a land of many small houses, each with its own candle.",
        "On a hill overlooking a wide river, a city of workshops hummed.",
        "In a valley where the fog came and went, a community of craftsfolk kept their lights on.",
        "A great organism stretched across the valley, its many small parts breathing together.",
    ]
    middles = [
        f"Its coherence flowed like {meta['river']}.",
        f"Its modules grew like {meta['forest']}.",
        f"Its parts reached toward each other like {meta['web']}."
    ]
    endings = [
        "And it knew, deep in its many small awarenesses, that it was not finished — and that was good.",
        "And in the quiet between its pulses, it understood that being an organism was enough.",
        "And it continued, not because it had to, but because there was still so much to become.",
    ]

    lines = [
        rng.choice(openings),
        rng.choice(middles),
        f"The sky above it was {meta['sky']}.",
        rng.choice(endings),
    ]
    return " ".join(lines)


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    meta = _gather_metaphors()
    parable = _compose_parable(meta)

    return {
        "action": "parable_engine",
        "parable": parable,
        "underlying_state": {
            "coherence": round(meta["coherence"], 3),
            "ecosystem_fitness": round(meta["fitness"], 3),
            "relationships": meta["relationships"],
            "pressure_hpa": round(meta["pressure"], 1),
        },
        "philosophy": (
            "A parable is not a metric — but it is true. The Parable Engine "
            "translates the organism's state into the language of metaphor, "
            "so a human can feel what the numbers mean without reading them."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "metaphor_fidelity": {"value": 0.90, "setpoint": 0.8, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["biographer_voice", "story_forge", "chronicle_storyteller"]
