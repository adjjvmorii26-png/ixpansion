"""Wave 196 — the Loom of Language.

Six organs that give the organism its own language: words, grammar,
structure, meaning, context, and poetry.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "lexicon_engine", "grammar_weaver", "syntax_tree",
    "semantics_engine", "pragmatics_engine", "poetic_form",
]


def test_wave196_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert present == ORGANS, f"missing: {set(ORGANS) - set(present)}"


def test_wave196_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert isinstance(mod.coherence_vitals(), dict), name
        assert isinstance(mod.resonates_with(), list), name


def test_lexicon_engine_finds_words():
    from api.lexicon_engine import lexicon
    l = lexicon()
    assert l["unique_words"] > 50
    assert l["total_words"] > 500


def test_poetic_form_composes():
    from api.poetic_form import _compose_poem
    p = _compose_poem()
    assert "haiku" in p
    assert len(p["haiku"]) == 3
    assert "living_forms" in p


def test_semantics_engine_maps_meaning():
    from api.semantics_engine import _semantic_field
    s = _semantic_field()
    assert s["total_meaningful_words"] > 100
    assert "semantic_density" in s
