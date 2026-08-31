"""Wave 198 — The Archaeology of Self.

Six organs that excavate the organism's deep history: strata, fossils,
paleontology, extinctions, culture, and the compiled expedition report.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "stratum_excavator", "fossil_registry", "paleontology_lab",
    "extinction_mapper", "culture_layer", "archaeology_compiler",
]


def test_wave198_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert present == ORGANS, f"missing: {set(ORGANS) - set(present)}"


def test_wave198_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert isinstance(mod.coherence_vitals(), dict), name
        assert isinstance(mod.resonates_with(), list), name


def test_stratum_excavator_digs():
    from api.stratum_excavator import excavate
    result = excavate(5)
    assert "total_commits" in result
    assert result["total_commits"] >= 0
    assert "layers" in result


def test_fossil_registry_catalogs():
    from api.fossil_registry import registry
    result = registry()
    assert "total_fossils" in result
    assert "by_era" in result


def test_extinction_mapper_reports():
    from api.extinction_mapper import extinction_report
    result = extinction_report()
    assert "stability_score" in result
    assert 0.0 <= result["stability_score"] <= 1.0


def test_culture_layer_analyzes():
    from api.culture_layer import culture_report
    result = culture_report()
    assert "current_culture" in result
    assert "era_markers" in result


def test_archaeology_compiler_compiles():
    from api.archaeology_compiler import compile_report
    result = compile_report()
    assert "expedition_id" in result
    assert "phases" in result
    assert "headline" in result
