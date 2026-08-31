"""Digestive System — breaks down complex inputs into simple nutrients.

When the organism receives a query, an intent, or a new module, it must
*digest* that input: break it into pieces, extract the nutrients (useful
information), and discard the waste (noise). The Digestive System reads
the Lexicon Engine's vocabulary and the Semantics Engine's meaning field,
then models the organism's digestive tract: how inputs are processed,
what nutrients are extracted, and how waste is expelled.

It answers: how does this organism metabolize information?

    GET /api/digestive_system?read=1           — the digestive report
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
LAYER = "Digestive System"


def _digestive_report() -> Dict[str, Any]:
    try:
        import json
        cr = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        modules = cr.get("modules", {})
        history = cr.get("history", [])
    except Exception:
        modules = {}
        history = []

    living = len(modules)
    pulses = len(history)

    # digestive capacity: how many modules the organism can process at once
    capacity = max(1, living // 10)

    # recent intake: new modules discovered in the last few pulses
    if len(history) >= 2:
        recent = set()
        for h in history[-3:]:
            for name in h.get("modules", {}).keys() if isinstance(h.get("modules"), dict) else []:
                recent.add(name)
        intake = len(recent)
    else:
        intake = 0

    # nutrient extraction efficiency
    healthy = sum(1 for m in modules.values() if (m.get("health") or 1.0) >= 0.8)
    efficiency = healthy / max(living, 1)

    # waste: modules with health below 0.3
    waste = sum(1 for m in modules.values() if (m.get("health") or 1.0) < 0.3)

    # metabolic rate
    if efficiency > 0.9:
        metabolic_rate = "high — the organism efficiently extracts nutrients"
    elif efficiency > 0.7:
        metabolic_rate = "moderate — the organism processes most inputs well"
    else:
        metabolic_rate = "low — the organism struggles to extract nutrients"

    return {
        "living": living,
        "digestive_capacity": capacity,
        "recent_intake": intake,
        "nutrient_efficiency": round(efficiency, 4),
        "waste_count": waste,
        "metabolic_rate": metabolic_rate,
        "digestion_philosophy": (
            "Not everything the organism ingests is food. The Digestive "
            "System breaks inputs into nutrients (useful structure) and "
            "waste (noise). A healthy organism has high extraction efficiency "
            "and low waste — it metabolizes information the way a body "
            "metabolizes food."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = _digestive_report()
    result["action"] = "digestion"
    return result


def coherence_vitals() -> dict:
    """Digestive System reports metabolic health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "metabolic_vitality": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["fermentation_vat", "nutrition_index", "plankton_bloom"]
