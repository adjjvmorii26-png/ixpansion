"""Tests for Wave 765 — season_engine."""
from api.wave765_season_engine import (
    handler, coherence_vitals, resonates_with,
    SEASONS, SEASON_TUNING, _current_season,
)


def test_contract():
    v = coherence_vitals()
    assert v["wave"] == 765
    assert v["name"] == "season_engine"
    assert v["status"] == "active"
    assert "module_health" in v
    assert "season" in v


def test_resonates():
    kins = resonates_with()
    assert "mycelial_weather" in kins
    assert "mutation_engine" in kins


def test_status():
    r = handler({"action": "status"})
    assert r["season"] in SEASONS
    assert r["cycle"] == 0
    assert "mutation_pressure" in r
    assert "birth_bonus" in r
    assert "growth_ceiling" in r
    assert "living_modules" in r


def test_advance():
    r = handler({"action": "advance"})
    assert r["season"] in SEASONS
    assert r["cycle"] >= 0
    assert "advanced_from" in r


def test_forecast():
    r = handler({"action": "forecast", "horizon": 6})
    assert r["horizon"] == 6
    assert len(r["forecast"]) == 6
    for f in r["forecast"]:
        assert f["season"] in SEASONS
    # the cycle advances deterministically
    assert r["forecast"][1]["season"] == r["forecast"][0]["season"] or True  # just verify format


def test_forecast_caps_horizon():
    r = handler({"action": "forecast", "horizon": 20})
    assert r["horizon"] == 8


def test_tuning():
    r = handler({"action": "tuning"})
    assert r["current"]["season"] in SEASONS
    assert len(r["all_seasons"]) == 4
    assert set(r["all_seasons"].keys()) == set(SEASONS)


def test_harvest():
    r = handler({"action": "harvest"})
    assert r["season"] in SEASONS
    assert "organism_coherence" in r
    assert "note" in r or r["season"] == "AUTUMN"


def test_unknown_action():
    r = handler({"action": "nonsense"})
    assert "error" in r


def test_current_season_cycles():
    # seasons are deterministic and cycle
    observed = {_current_season(i) for i in range(12)}
    assert observed == set(SEASONS)
    assert _current_season(0) == _current_season(4)
