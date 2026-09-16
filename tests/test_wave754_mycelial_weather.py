"""Tests for Wave 754 — mycelial_weather."""
from __future__ import annotations

from api.wave754_mycelial_weather import (
    NAME,
    WAVE,
    coherence_vitals,
    handler,
    resonates_with,
)


def test_contract():
    assert callable(handler)
    assert callable(coherence_vitals)
    assert isinstance(resonates_with(), list)


def test_ping():
    out = handler({"action": "ping"})
    assert out["ok"] is True
    assert out["alive"] is True


def test_status():
    out = handler({"action": "status"})
    assert out["ok"] is True
    assert out["wave"] == WAVE
    assert out["name"] == NAME
    assert out["organs"] > 100
    assert "biomes" in out


def test_forecast():
    out = handler({"action": "forecast", "days": 7})
    assert out["ok"] is True
    assert out["days"] == 7
    assert len(out["series"]) == 7
    assert "advisory" in out


def test_forecast_caps_days():
    out = handler({"action": "forecast", "days": 999})
    assert out["ok"] is True
    assert out["days"] == 30


def test_currents():
    out = handler({"action": "currents"})
    assert out["ok"] is True
    assert "fertile" in out
    assert "scarce" in out


def test_nutrients():
    out = handler({"action": "nutrients"})
    assert out["ok"] is True
    assert len(out["biomes"]) >= 1
    assert "coverage" in out


def test_unknown_action():
    out = handler({"action": "not_real"})
    assert out["ok"] is False
    assert out["error"] == "unknown_action"


def test_coherence_vitals():
    v = coherence_vitals()
    assert v["wave"] == WAVE
    assert v["status"] == "active"
    assert v["resonance"] > 0
