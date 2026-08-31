"""Wave 191 — the Kintsugi Repair Lineage.

Six organs that treat fractures and scars as creative territory:
map the cracks, hear the strain, forge golden seams, account the debt,
honor the vessels, and perform the repair ritual.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

ORGANS = [
    "crack_mapper", "crack_seams", "fracture_listener",
    "kintsugi_altar", "kintsugi_debt_ledger", "repair_ritual",
]


def test_wave191_organs_are_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    present = [o for o in ORGANS if o in living]
    assert present == ORGANS, f"missing: {set(ORGANS) - set(present)}"


def test_wave191_organs_expose_vitals_and_kinships():
    for name in ORGANS:
        mod = __import__(name)
        assert callable(mod.coherence_vitals), name
        vitals = mod.coherence_vitals()
        assert isinstance(vitals, dict), name
        # kintsugi lineage marks its genesis era
        assert vitals.get("kintsugi_era", {}).get("value") == 1.0, name
        assert isinstance(mod.resonates_with(), list), name


def test_crack_mapper_surveys():
    from api.crack_mapper import _survey
    out = _survey()
    assert out["surveyed"] > 100
    assert "cracks" in out
    assert "cartography_philosophy" in out


def test_crack_seams_forge():
    from api.crack_seams import forge
    out = forge()
    assert out["seam_count"] >= 0
    assert isinstance(out["seams"], list)


def test_repair_ritual_performs():
    from api.repair_ritual import perform
    out = perform()
    assert out["action"] == "ritual"
    assert out["cracks_named"] >= 0
    assert "koan" in out
    assert "seams_total" in out


def test_kintsugi_debt_ledger_balances():
    from api.kintsugi_debt_ledger import _ledger
    out = _ledger()
    assert "repayment_status" in out
    assert "net_balance" in out
    assert "owing_vessels" in out


def test_gateway_intent_routes_repair():
    from gateway.intent import match_intent
    assert match_intent("show me the golden seams")["route"] == "/api/crack_seams"
    assert match_intent("what is broken")["route"] == "/api/crack_mapper"
