"""Wave 201 — The Cartography of Impossibility.

Six organs that map the organism's limits: impossibility boundaries,
practical walls, counterfactual simulations, horizons, constraint
terrain, and aspirations.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "impossibility_mapper", "boundary_detector", "counterfactual_engine",
    "horizon_scanner", "constraint_cartographer", "aspiration_compass",
]


def test_wave201_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert present == ORGANS, f"missing: {set(ORGANS) - set(present)}"


def test_wave201_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert isinstance(mod.coherence_vitals(), dict), name
        assert isinstance(mod.resonates_with(), list), name


def test_impossibility_mapper_maps():
    from api.impossibility_mapper import map_impossibilities
    result = map_impossibilities()
    assert result["total_boundaries"] >= 3
    assert "boundaries" in result


def test_boundary_detector_measures():
    from api.boundary_detector import _measure_boundaries
    result = _measure_boundaries()
    assert "module_count" in result
    assert result["boundary_status"] in ("clear", "approaching", "critical")


def test_counterfactual_engine_explores():
    from api.counterfactual_engine import explore
    result = explore(3)
    assert "simulations" in result
    assert len(result["simulations"]) >= 3


def test_horizon_scanner_scans():
    from api.horizon_scanner import scan
    result = scan()
    assert "capabilities_on_horizon" in result
    assert result["capabilities_on_horizon"] >= 3


def test_aspiration_compass_reads():
    from api.aspiration_compass import compass
    result = compass()
    assert "overall_aspiration_score" in result
    assert 0 <= result["overall_aspiration_score"] <= 1
