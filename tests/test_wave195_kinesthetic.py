"""Wave 195 — the Kinesthetic Engine.

Six organs that make the organism move: motion, gesture, body map,
momentum, dance, and stillness.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "kinesthetic_engine", "gesture_synthesizer", "proprioception",
    "momentum_tracker", "dance_composer", "stillness_meditator",
]


def test_wave195_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert present == ORGANS, f"missing: {set(ORGANS) - set(present)}"


def test_wave195_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert isinstance(mod.coherence_vitals(), dict), name
        assert isinstance(mod.resonates_with(), list), name


def test_kinesthetic_engine_reads_motion():
    from api.kinesthetic_engine import _kinesthetic_state
    k = _kinesthetic_state()
    assert "motion" in k
    assert "velocity" in k
    assert "direction" in k


def test_gesture_synthesizer_synthesizes():
    from api.gesture_synthesizer import _synthesize_gesture
    g = _synthesize_gesture()
    assert "gesture" in g
    assert g["gesture"] in ("reach","recoil","gather","scatter","turn","settle","surge","drift","still")


def test_momentum_tracker_computes():
    from api.momentum_tracker import _momentum
    m = _momentum()
    assert "mass" in m
    assert "velocity" in m
    assert "momentum_magnitude" in m
