"""Wave 199 — The Meteorology of Thought.

Six organs that give the organism its own cognitive weather system:
barometric intent, fronts, precipitation, jet streams, climate, and storms.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "barometric_intent", "front_tracker", "precipitation_cycle",
    "jet_stream_attention", "climate_memory", "storm_chaser",
]


def test_wave199_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert present == ORGANS, f"missing: {set(ORGANS) - set(present)}"


def test_wave199_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert isinstance(mod.coherence_vitals(), dict), name
        assert isinstance(mod.resonates_with(), list), name


def test_barometric_intent_reads_pressure():
    from api.barometric_intent import _compute_pressure
    p = _compute_pressure()
    assert "pressure_hpa" in p
    assert 0 < p["pressure_hpa"] < 2000


def test_front_tracker_detects_fronts():
    from api.front_tracker import _analyze_fronts
    fronts = _analyze_fronts()
    assert len(fronts) >= 3
    assert all("front_type" in f for f in fronts)


def test_precipitation_cycle_measures():
    from api.precipitation_cycle import _measure_cycle
    cycle = _measure_cycle()
    assert "condensation_rate" in cycle
    assert 0 <= cycle["condensation_rate"] <= 1


def test_climate_memory_analyzes():
    from api.climate_memory import _analyze_climate
    climate = _analyze_climate()
    assert "climate_type" in climate
    assert "months_observed" in climate


def test_storm_chaser_detects():
    from api.storm_chaser import _detect_storms
    storms = _detect_storms()
    assert isinstance(storms, list)
