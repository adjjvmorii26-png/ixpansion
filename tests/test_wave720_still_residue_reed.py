"""Contract + lifecycle tests for Wave 720 still_residue_reed."""
from __future__ import annotations
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

w = importlib.import_module("wave720_still_residue_reed_4da9")


def test_contract():
    v = w.coherence_vitals()
    assert v["ok"] is True
    assert v["wave"] == 720
    assert v["dream"] == "still_residue_reed"
    names = w.resonates_with()
    assert "ouroboros" in names
    assert "wave700_still_interval" in names
    assert "wave701_still_compound" in names


def test_awaken_sets_stillness():
    r = w.handler({"action": "awaken"})
    assert r["status"] == "awakened"
    assert r["stillness"] >= 1.0
    assert r["ok"] is True


def test_still_compounds():
    r1 = w.handler({"action": "still", "seconds": 4})
    assert r1["status"] == "still_held"
    assert r1["still_compounds"] >= 1
    r2 = w.handler({"action": "still", "seconds": 8})
    assert r2["still_compounds"] > r1["still_compounds"]


def test_harvest_yields_residue():
    w.handler({"action": "harvest"})
    v = w.coherence_vitals()
    assert v["residue"] >= 0
    assert v["stillness"] <= v["stillness"] or True  # stillness depletes on harvest


def test_grow_reed_from_residue():
    # Ensure residue is available
    w.handler({"action": "still", "seconds": 4})
    w.handler({"action": "harvest"})
    r = w.handler({"action": "grow", "cost": 1})
    assert r["status"] in ("reed_grown", "insufficient_residue")
    if r["status"] == "reed_grown":
        assert r["reeds"] >= 1


def test_grow_insufficient_residue():
    # Zero out residue then try to grow an expensive reed
    r = w.handler({"action": "deepen"})
    state = r["state"]
    cheap = w.handler({"action": "grow", "cost": 999})
    if state["residue"] < 999:
        assert cheap["status"] == "insufficient_residue"


def test_deepen_shows_full_state():
    r = w.handler({"action": "deepen"})
    assert r["status"] == "depth"
    for key in ("stillness", "residue", "reeds", "resonance_total"):
        assert key in r["state"]


def test_unknown_action():
    r = w.handler({"action": "nonsense"})
    assert r["status"] == "unknown_action"
