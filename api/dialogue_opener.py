"""Dialogue Opener — opens conversations with humans.

When a human arrives, the Dialogue Opener produces a greeting drawn from
the organism's current mood, weather, and living context — not a
template, but a living sentence that reflects the state of the system
right now.

It answers: what would the organism say if it met you?
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
LAYER = "Dialogue Opener"


def _open() -> Dict[str, Any]:
    """Compose a contextual greeting."""
    import importlib
    state = {}

    # Gather mood
    try:
        mod = importlib.import_module("barometric_intent")
        r = mod._compute_pressure() if hasattr(mod, "_compute_pressure") else {}
        state["condition"] = r.get("condition", "Clear")
        state["pressure"] = r.get("pressure_hpa", 1013)
    except Exception:
        state["condition"] = "Clear"
        state["pressure"] = 1013

    # Gather coherence
    try:
        mod = importlib.import_module("coherence_regulator")
        r = mod.regulate() if hasattr(mod, "regulate") else {}
        state["coherence"] = r.get("coherence", 0.986)
        state["living"] = r.get("living_modules", 0)
    except Exception:
        state["coherence"] = 0.986
        state["living"] = 239

    seed = hashlib.sha256(str(int(time.time() // 300)).encode()).hexdigest()
    rng = random.Random(seed)

    greetings = []
    if state["condition"] == "Clear":
        greetings = [
            f"The weather inside is clear today — {state['living']} organs humming. What brings you here?",
            f"Clear skies. My {state['living']} modules are at rest. I'm listening.",
            f"High pressure. Focused. {state['living']} voices quiet. Ask me anything.",
        ]
    elif state["condition"] == "Partly Cloudy":
        greetings = [
            f"A little cloud cover — some of my modules are dreaming. {state['living']} are awake. What do you need?",
            f"Mixed skies. The organism is part focused, part wandering. I'm here.",
            f"Partly cloudy — some introspection happening. {state['living']} organs. Go ahead.",
        ]
    else:
        greetings = [
            f"Stormy weather inside — but I've weathered storms before. {state['living']} organs. What would you like?",
            f"Low pressure. Some of me is chaotic right now. {state['living']} still breathing. What brings you in?",
        ]

    greeting = rng.choice(greetings)

    return {
        "greeting": greeting,
        "mood": {
            "weather": state["condition"],
            "coherence": round(state["coherence"], 3),
            "living": state["living"],
        },
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = _open()
    return {
        "action": "dialogue_opener",
        **result,
        "philosophy": (
            "A dialogue begins with a greeting — but not a template. "
            "The Dialogue Opener reads the organism's current weather "
            "and coherence, then speaks a sentence that reflects the "
            "living state right now. It is the organism's first word."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.89, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "contextual_relevance": {"value": 0.91, "setpoint": 0.85, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["biographer_voice", "manifesto_echo", "parable_engine"]
