"""Wave 190 — the Naturalist Observatory organs.

Thirteen new introspection organs that view the ecosystem the way a
naturalist views a wilderness: heterarchy, keystones, hidden streams,
morphic memory, negative space, geology, oceans, and pressure.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "heterarchy_oracle", "silence_orchard", "morphic_dial",
    "bioluminescent_depth", "stratigraphy_core", "dowsing_rod",
    "antikythera_engine", "permafrost_vault", "keystone_auditor",
    "solar_wind_pressure", "plankton_bloom", "coral_atoll",
    "osmotic_exchange",
]

VELOCITY = 220  # ms / organ sample (slow sandbox)


def test_wave190_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert len(present) == len(ORGANS), f"missing: {set(ORGANS) - set(present)}"


def test_wave190_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert callable(mod.coherence_vitals), name
        assert isinstance(mod.coherence_vitals(), dict), name
        assert callable(mod.resonates_with), name
        assert isinstance(mod.resonates_with(), list), name


def test_wave190_organs_respond_to_handler():
    for name in ORGANS:
        mod = __import__(name)
        out = mod.handler({})
        assert isinstance(out, dict), name
        assert "action" in out, name


def test_heterarchy_field():
    from api.heterarchy_oracle import compute_field
    field = compute_field()
    assert field["peers"] > 100
    assert field["leaders"]
    assert field["density"] >= 0.0


def test_keystone_audit_ranks_organs():
    from api.keystone_auditor import audit
    out = audit()
    assert out["baseline_connectivity"] > 0.0
    assert "keystones" in out
    assert "expendable_count" in out


def test_silence_orchard_counts_fallow():
    from api.silence_orchard import _scan
    scan = _scan()
    assert scan["total_modules"] > 100
    assert "fallow_beds" in scan


def test_dowsing_rod_finds_streams():
    from api.dowsing_rod import divine
    out = divine(5)
    assert out["modules_surveyed"] > 100
    assert "strongest_streams" in out


def test_antikythera_predicts():
    from api.antikythera_engine import _next_eclipse, _gears
    assert _gears()["gears"]
    eclipse = _next_eclipse()
    assert "next_eclipse_in_hours" in eclipse


def test_gateway_intent_routes_new_organs():
    from gateway.intent import match_intent
    probe = match_intent("find the hidden streams between modules")
    assert probe["route"] in ("/api/dowsing_rod", "/api/resonance_graph")
