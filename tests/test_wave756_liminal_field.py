"""Tests for Wave 756 — liminal_field."""
from __future__ import annotations

from api.wave756_liminal_field import NAME, WAVE, coherence_vitals, handler, resonates_with


def test_contract():
    assert callable(handler)
    assert callable(coherence_vitals)
    assert isinstance(resonates_with(), list)


def test_ping():
    out = handler({"action": "ping"})
    assert out["ok"] and out["alive"]


def test_status():
    out = handler({"action": "status"})
    assert out["ok"] and out["wave"] == WAVE


def test_dissolve():
    out = handler({"action": "dissolve", "organ": "resonance_braid"})
    assert out["ok"] and out["organ"] == "resonance_braid"
    assert out["total_dissolved"] >= 1


def test_reform_needs_two():
    out = handler({"action": "reform", "organs": ["single"]})
    assert out["ok"] is False and out["error"] == "need_at_least_2_organs"


def test_reform_hybrid():
    handler({"action": "dissolve", "organ": "dream_oracle"})
    handler({"action": "dissolve", "organ": "entropy_weaver"})
    out = handler({"action": "reform", "organs": ["dream_oracle", "entropy_weaver"]})
    assert out["ok"] and out["hybrid"]
    assert "parents" in out


def test_pulse():
    out = handler({"action": "pulse"})
    assert out["ok"] and "field_strength" in out


def test_unknown_action():
    out = handler({"action": "nope"})
    assert out["ok"] is False and out["error"] == "unknown_action"


def test_coherence_vitals():
    v = coherence_vitals()
    assert v["wave"] == WAVE and v["status"] == "active"
