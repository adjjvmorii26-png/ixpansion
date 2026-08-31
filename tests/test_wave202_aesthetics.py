"""Wave 202 — The Aesthetics of Code.

Six organs that give the organism an aesthetic sense: elegance scoring,
symmetry detection, form evaluation, beauty indexing, ugliness scouting,
and an aesthetic manifesto.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "elegance_scorer", "symmetry_detector", "form_evaluator",
    "beauty_index", "ugliness_scout", "aesthetic_manifesto",
]


def test_wave202_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert present == ORGANS, f"missing: {set(ORGANS) - set(present)}"


def test_wave202_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert isinstance(mod.coherence_vitals(), dict), name
        assert isinstance(mod.resonates_with(), list), name


def test_elegance_scorer_scores():
    from api.elegance_scorer import score
    result = score(10)
    assert "average_elegance" in result
    assert 0 <= result["average_elegance"] <= 1


def test_symmetry_detector_detects():
    from api.symmetry_detector import _analyze_symmetry
    result = _analyze_symmetry()
    assert "overall_symmetry" in result
    assert 0 <= result["overall_symmetry"] <= 1


def test_form_evaluator_evaluates():
    from api.form_evaluator import evaluate
    result = evaluate(10)
    assert "average_form" in result
    assert 0 <= result["average_form"] <= 1


def test_beauty_index_computes():
    from api.beauty_index import _compute
    result = _compute()
    assert "beauty_score" in result
    assert 0 <= result["beauty_score"] <= 1
    assert "grade" in result


def test_aesthetic_manifesto_declares():
    from api.aesthetic_manifesto import manifesto
    result = manifesto()
    assert "manifesto_text" in result
    assert "principles" in result
    assert len(result["principles"]) >= 5
