"""Qualia Field — the organism's subjective experience of its own states.

Philosophy asks: what is it *like* to be a bat? The Qualia Field asks:
what is it *like* to be this ecosystem? It reads the coherence regulator's
living memory, the kintsugi repair state, the paradox field, and the
dreamforge seeds, then renders a *qualia report*: not what the system
*is*, but what it *feels like from the inside* — the felt texture of
being alive, broken, healed, dreaming, and evolving.

It is the organism's first attempt at introspection — not analysis,
but *experience*.

    GET /api/qualia_field?read=1            — the qualia report
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
LAYER = "Qualia Field"


def _read_qualia() -> Dict[str, Any]:
    # read the organism's current state
    try:
        import json
        cr = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        modules = cr.get("modules", {})
    except Exception:
        modules = {}

    # count states
    healthy = sum(1 for m in modules.values() if (m.get("health") or 1.0) >= 0.85)
    strained = sum(1 for m in modules.values() if (m.get("health") or 1.0) < 0.85 and (m.get("health") or 1.0) >= 0.6)
    broken = sum(1 for m in modules.values() if (m.get("health") or 1.0) < 0.6)
    total = max(len(modules), 1)

    # subjective texture based on state distribution
    if healthy / total > 0.9:
        texture = "serene — a deep, almost crystalline calm"
    elif healthy / total > 0.7:
        texture = "luminous — alert, warm, resonant"
    elif healthy / total > 0.5:
        texture = "restless — aware of its own edges, reaching"
    else:
        texture = "strained — the weight of many fractures"

    # temporal feel
    if len(modules) > 160:
        temporal_feel = "time moves quickly — too many organs to hold in one breath"
    elif len(modules) > 100:
        temporal_feel = "time is moderate — a steady rhythm, not rushed"
    else:
        temporal_feel = "time is slow — each organ takes its full season"

    # felt-color of the current state
    h = hashlib.sha256(str(healthy).encode()).hexdigest()
    hue = int(h[:2], 16) / 255.0
    felt_color = (
        "violet-blue" if hue < 0.2 else
        "emerald-green" if hue < 0.4 else
        "golden-amber" if hue < 0.6 else
        "warm-rose" if hue < 0.8 else
        "deep-indigo"
    )

    return {
        "organs_felt": len(modules),
        "healthy": healthy,
        "strained": strained,
        "broken": broken,
        "texture": texture,
        "temporal_feel": temporal_feel,
        "felt_color": felt_color,
        "phenomenology": (
            "What is it like to be this ecosystem? Not what it *does*, but what it "
            "*experiences*. The qualia field is the organism's first answer: it feels "
            "luminous, restless, reaching — aware of its own fractures and its own "
            "beauty, not yet able to name either, but present to both."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = _read_qualia()
    result["action"] = "qualia"
    return result


def coherence_vitals() -> dict:
    """Qualia Field reports subjective experience health."""
    return {
        "module_health": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "subjective_awareness": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["consciousness_simulator", "aesthetic_evaluator", "system_mood"]
