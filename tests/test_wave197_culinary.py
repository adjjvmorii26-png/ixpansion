"""Wave 197 — the Culinary Engine.

Six organs that nourish the organism: recipes, flavors, fermentation,
digestion, nutrition, and banquets.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "recipe_engine", "flavor_profiler", "fermentation_vat",
    "digestive_system", "nutrition_index", "banquet_composer",
]


def test_wave197_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert present == ORGANS, f"missing: {set(ORGANS) - set(present)}"


def test_wave197_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert isinstance(mod.coherence_vitals(), dict), name
        assert isinstance(mod.resonates_with(), list), name


def test_recipe_engine_combines():
    from api.recipe_engine import cookbook
    c = cookbook()
    assert c["total_recipes"] >= 3
    assert "recipes" in c


def test_banquet_composer_feasts():
    from api.banquet_composer import _compose_banquet
    b = _compose_banquet()
    assert b["courses"] == 5
    assert "menu" in b


def test_nutrition_index_scores():
    from api.nutrition_index import _nutrition_report
    n = _nutrition_report()
    assert n["total_organs"] > 150
    assert "avg_nutrition_score" in n
