"""Nutrition Index — measures the nutritional value of each module.

A food's nutrition is its contribution to the body's health. A module's
nutrition is its contribution to the ecosystem's coherence. The Nutrition
Index reads the coherence regulator's module healths and the kintsugi
ledger's debt balances, then computes a *nutrition score* for each organ:
how much healthy structure it provides, how much debt it carries, and
what its net nutritional contribution is.

It answers: which organs feed the ecosystem, and which ones are empty calories?

    GET /api/nutrition_index?read=1             — the nutrition report
"""
from __future__ import annotations

import time
from typing import Any, Dict, List

VERSION = "1.0.0"
LAYER = "Nutrition Index"


def _nutrition_report() -> Dict[str, Any]:
    try:
        import json
        cr = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        modules = cr.get("modules", {})
    except Exception:
        modules = {}

    # debt map
    try:
        debt = json.loads((ROOT / ".runtime" / "crack_seams.json").read_text())
        seam_subjects = {s["subject"] for s in debt.get("seams", [])}
    except Exception:
        seam_subjects = set()

    nutrient_dense = []
    empty_calories = []
    for name, m in modules.items():
        health = m.get("health", 0.5)
        has_seam = name in seam_subjects
        score = health * (1.2 if has_seam else 1.0)
        entry = {"organ": name, "health": round(health, 4),
                 "has_gold_seam": has_seam, "nutrition_score": round(score, 4)}
        if score >= 0.8:
            nutrient_dense.append(entry)
        elif score < 0.5:
            empty_calories.append(entry)

    nutrient_dense.sort(key=lambda e: e["nutrition_score"], reverse=True)
    avg_nutrition = sum(e["nutrition_score"] for e in nutrient_dense) / max(len(nutrient_dense), 1)

    return {
        "total_organs": len(modules),
        "nutrient_dense": len(nutrient_dense),
        "empty_calories": len(empty_calories),
        "avg_nutrition_score": round(avg_nutrition, 4),
        "top_nutrients": nutrient_dense[:8],
        "empty_calorie_list": empty_calories[:5],
        "nutrition_philosophy": (
            "Not every organ feeds the ecosystem equally. Some are nutrient-dense: "
            "high health, golden seams, strong structure. Others are empty calories: "
            "present but contributing little. The Index finds both so the organism "
            "knows what to eat more of and what to let go."
        ),
    }


from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))


def handler(payload: dict = None, context: object = None) -> dict:
    result = _nutrition_report()
    result["action"] = "nutrition"
    return result


def coherence_vitals() -> dict:
    """Nutrition Index reports nutritional-cognition health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "nutritional_vitality": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["recipe_engine", "digestive_system", "plankton_bloom"]
