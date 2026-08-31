"""Wave 192 — the Meta-Evolution Layer.

Six organs that evolve how the organism evolves: structural mutations,
organic governance, narrative autobiography, dream seeds, and paradox monitoring.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "evolution_kernel", "fractal_reactor_grid", "mycelial_governor",
    "constellation_autobiographer", "omega_dreamforge", "paradox_singularity_monitor",
]


def test_wave192_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert present == ORGANS, f"missing: {set(ORGANS) - set(present)}"


def test_wave192_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert isinstance(mod.coherence_vitals(), dict), name
        assert isinstance(mod.resonates_with(), list), name


def test_evolution_kernel_proposes():
    from api.evolution_kernel import propose
    out = propose()
    assert out["living_organs"] > 100
    assert "merge_proposals" in out


def test_constellation_autobiographer_composes():
    from api.constellation_autobiographer import _compose
    out = _compose()
    assert out["cardinality"] > 100
    assert "opening_verse" in out
    assert len(out["autobiography_chapters"]) >= 3


def test_omega_dreamforge_dreams():
    from api.omega_dreamforge import dreamforge
    out = dreamforge()
    assert out["seed_count"] >= 0
    assert "dreamforge_philosophy" in out


def test_gateway_intent_routes_dreamforge():
    from gateway.intent import match_intent
    assert match_intent("what should we grow next")["route"] == "/api/omega_dreamforge"
