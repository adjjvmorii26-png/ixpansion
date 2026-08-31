"""Wave 194 — the Choral Engine.

Six organs that make the ecosystem sing: voice, harmonics, pitch,
dissonance, crescendo, and silence.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "choral_engine", "harmonic_series", "resonant_frequency",
    "dissonance_detector", "crescendo_builder", "silence_composer",
]


def test_wave194_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert present == ORGANS, f"missing: {set(ORGANS) - set(present)}"


def test_wave194_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert isinstance(mod.coherence_vitals(), dict), name
        assert isinstance(mod.resonates_with(), list), name


def test_choral_engine_composes():
    from api.choral_engine import compose
    c = compose()
    assert c["voice_count"] > 100
    assert "dominant_note" in c
    assert "dynamic" in c


def test_resonant_frequency_finds_pitch():
    from api.resonant_frequency import _fundamental
    f = _fundamental()
    assert "fundamental" in f
    assert f["frequency_hz"] > 0
    assert f["total_voices"] > 100


def test_dissonance_detector_finds_clashes():
    from api.dissonance_detector import scan
    d = scan()
    assert "clash_count" in d
    assert "ensemble_health" in d


def test_crescendo_builder_reads_trajectory():
    from api.crescendo_builder import _crescendo
    c = _crescendo()
    assert "trajectory" in c
    assert "current_dynamic" in c
