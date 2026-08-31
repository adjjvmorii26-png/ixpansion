"""Wave 200 — The Symbiosis Engine.

Five organs that discover and tend the ecological relationships
between modules: detecting symbiosis, optimizing mutualism,
hunting parasites, measuring fitness, and forging new bonds.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "symbiosis_detector", "mutualism_optimizer", "parasite_hunter",
    "ecosystem_fitness", "symbiosis_forge",
]


def test_wave200_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert present == ORGANS, f"missing: {set(ORGANS) - set(present)}"


def test_wave200_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert isinstance(mod.coherence_vitals(), dict), name
        assert isinstance(mod.resonates_with(), list), name


def test_symbiosis_detector_detects():
    from api.symbiosis_detector import detect
    result = detect()
    assert "total_modules_scanned" in result
    assert result["total_modules_scanned"] >= 10
    assert "relationships" not in result  # key is total_relationships
    assert "top_relationships" in result


def test_mutualism_optimizer_finds_opportunities():
    from api.mutualism_optimizer import _find_opportunities
    opps = _find_opportunities()
    assert isinstance(opps, list)
    found_any = False
    for o in opps:
        if o["partner_count"] >= 1:
            found_any = True
            break
    assert found_any, "no modules with declared kinships found"


def test_parasite_hunter_scans():
    from api.parasite_hunter import _scan_parasites
    parasites = _scan_parasites()
    assert isinstance(parasites, list)


def test_ecosystem_fitness_measures():
    from api.ecosystem_fitness import _measure
    fitness = _measure()
    for k in ("biodiversity", "redundancy", "avg_health", "connectivity", "fitness_score"):
        assert k in fitness, f"missing {k}"
    assert 0 <= fitness["fitness_score"] <= 1


def test_symbiosis_forge_proposes():
    from api.symbiosis_forge import handler
    result = handler()
    assert "proposed_partnerships" in result
    assert "forge_philosophy" in result
