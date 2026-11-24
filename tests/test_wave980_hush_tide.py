"""Tests for wave980 hush_tide — pure, no network."""
from __future__ import annotations

from api.wave980_hush_tide import evaluate, hush_score, tide_phase, coherence_vitals


def test_still_when_quiet():
    r = evaluate({"gossip": 0.05, "forge": 0.05, "time": 0.05})
    assert r["tide"] == "STILL"
    assert r["product_surface"] == "hush"
    assert r["hush_score"] >= 0.72


def test_flood_when_loud():
    r = evaluate({"gossip": 0.95, "forge": 0.9, "time": 0.92})
    assert r["tide"] == "FLOOD"
    assert r["product_surface"] == "noise"


def test_clamps_garbage():
    r = evaluate({"gossip": "x", "forge": 99, "time": float("nan")})
    assert 0.0 <= r["hush_score"] <= 1.0
    assert r["tide"] in ("EBB", "SLACK", "FLOOD", "STILL")


def test_hush_inverse_of_pressure():
    quiet = hush_score(0.1, 0.1, 0.1)
    loud = hush_score(0.9, 0.9, 0.9)
    assert quiet > loud


def test_phase_boundaries():
    assert tide_phase(0.8) == "STILL"
    assert tide_phase(0.5) == "EBB"
    assert tide_phase(0.3) == "SLACK"
    assert tide_phase(0.1) == "FLOOD"


def test_coherence_vitals():
    v = coherence_vitals()
    assert v["wave"] == 980
    assert v["name"] == "hush_tide"
    assert v["layer"] == "organ"
    assert v["status"] == "active"
    assert "module_health" in v
    assert "phases" in v
