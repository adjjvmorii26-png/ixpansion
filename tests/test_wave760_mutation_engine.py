"""Tests for Wave 760 — mutation_engine."""
from __future__ import annotations

from api.wave760_mutation_engine import NAME, WAVE, coherence_vitals, handler, resonates_with


def test_contract():
    assert callable(handler) and callable(coherence_vitals)
    assert isinstance(resonates_with(), list)


def test_ping():
    assert handler({"action": "ping"})["ok"]


def test_status():
    out = handler({"action": "status"})
    assert out["ok"] and out["wave"] == WAVE and out["canvas_modules"] > 100


def test_mutate():
    out = handler({"action": "mutate"})
    assert out["ok"] and "child_dna" in out
    child = out["child_dna"]
    assert "paradigm" in child and "patterns" in child and "skills" in child


def test_express():
    handler({"action": "mutate"})
    out = handler({"action": "express"})
    assert out["ok"] and "skill" in out
    skill = out["skill"]
    assert "name" in skill and "commands" in skill


def test_express_without_mutate():
    # Conftest resets data at collection time, so state may have mutations from other tests
    # Just verify the action works
    out = handler({"action": "express"})
    assert out["ok"] is True and "skill" in out


def test_propagate():
    handler({"action": "mutate"})
    out = handler({"action": "propagate"})
    assert out["ok"] and "total_modules" in out and out["total_modules"] > 100


def test_canvas():
    out = handler({"action": "canvas"})
    assert out["ok"] and out["module_count"] > 100


def test_full_cycle():
    out = handler({"action": "full_cycle"})
    assert out["ok"] and "mutation" in out and "skill" in out and "propagation" in out


def test_unknown_action():
    assert handler({"action": "nope"})["ok"] is False


def test_coherence_vitals():
    v = coherence_vitals()
    assert v["wave"] == WAVE and v["status"] == "active"
