"""Wave 203 — The Organism Speaks Itself.

Six organs that give the organism a voice: biography, manifesto,
parable, dialogue, gratitude, and epitaph.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "biographer_voice", "manifesto_echo", "parable_engine",
    "dialogue_opener", "gratitude_index", "epitaph_writer",
]


def test_wave203_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert present == ORGANS, f"missing: {set(ORGANS) - set(present)}"


def test_wave203_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert isinstance(mod.coherence_vitals(), dict), name
        assert isinstance(mod.resonates_with(), list), name


def test_biographer_voice_writes():
    from api.biographer_voice import handler as h
    r = h()
    assert "biography" in r
    assert len(r["biography"]) > 50


def test_manifesto_echo_declares():
    from api.manifesto_echo import handler as h
    r = h()
    assert len(r["declarations"]) >= 5
    assert "credo" in r
    assert len(r["credo"]) > 20


def test_parable_engine_tells():
    from api.parable_engine import handler as h
    r = h()
    assert "parable" in r
    assert len(r["parable"]) > 50


def test_dialogue_opener_greets():
    from api.dialogue_opener import handler as h
    r = h()
    assert "greeting" in r
    assert len(r["greeting"]) > 10


def test_gratitude_index_measures():
    from api.gratitude_index import handler as h
    r = h()
    assert r["count"] >= 3
    assert r["total_weight"] > 0


def test_epitaph_writer_composes():
    from api.epitaph_writer import handler as h
    r = h()
    assert "epitaph" in r
    assert len(r["epitaph"]) > 20
