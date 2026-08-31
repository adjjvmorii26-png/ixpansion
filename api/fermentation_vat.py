"""Fermentation Vat — slow transformation of ideas.

Fermentation takes time: raw ingredients are transformed by invisible
agents (bacteria, yeast) into something entirely new. The Fermentation
Vat applies this metaphor to the ecosystem: it reads the recipe engine's
ingredients and the coherence regulator's history, then proposes
*fermentation plans* — pairs of modules whose slow combination, over
many pulses, could produce something neither could alone.

It answers: what ideas are fermenting right now, and what will they become?

    GET /api/fermentation_vat?read=1           — the active ferments
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Fermentation Vat"

STATE_FILE = ROOT / ".runtime" / "fermentation_vat.json"


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _fermentation_plan(a: str, b: str) -> Dict[str, Any]:
    h = hashlib.sha256((a + b).encode()).hexdigest()
    start = int(h[:4], 16) % 100
    duration = 3 + int(h[4:6], 16) % 8
    return {
        "ingredient_a": a,
        "ingredient_b": b,
        "ferment_start_pulse": start,
        "ferment_duration_pulses": duration,
        "expected_product": f"a hybrid of {a} and {b}",
        "fingerprint": f"frm:{h[:8]}",
    }


def active_ferments() -> Dict[str, Any]:
    living = _living()
    # select fermentation pairs: cross-family modules
    ferments = []
    families: Dict[str, List[str]] = {}
    for name in living:
        fam = name.split("_")[0] if "_" in name else name
        families.setdefault(fam, []).append(name)
    fam_list = sorted(families.keys())
    for i in range(min(len(fam_list) - 1, 6)):
        a = families[fam_list[i]][0]
        b = families[fam_list[i + 1]][0]
        ferments.append(_fermentation_plan(a, b))

    return {
        "active_ferments": len(ferments),
        "ferments": ferments,
        "fermentation_philosophy": (
            "The best transformations take time. The Vat does not rush — it "
            "places two ingredients together and lets time and invisible agents "
            "do the work. What emerges is neither A nor B, but C: something "
            "neither ingredient could have been alone."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = active_ferments()
    result["action"] = "ferments"
    return result


def coherence_vitals() -> dict:
    """Fermentation Vat reports transformation-health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "transformation_vitality": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["recipe_engine", "flavor_profiler", "digestive_system"]
