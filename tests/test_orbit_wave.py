from __future__ import annotations
"""Wave 448 — Orbit Cohesion Field test suite.

Exercises the eight orbital organs: cohesion fields, constellation mapping,
decay forecasts, anomaly oracles, pass synthesis, orbital storytelling,
debris mapping, and solar weather coupling.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

import orbit_cohesion_field
import noise_filter
import decay_forecaster
import telemetry_anomaly_oracle
import ground_station_synthesizer
import orbital_storyteller
import debris_field_mapper
import solar_weather_coupler

ORGANS = [
    orbit_cohesion_field,
    noise_filter,
    decay_forecaster,
    telemetry_anomaly_oracle,
    ground_station_synthesizer,
    orbital_storyteller,
    debris_field_mapper,
    solar_weather_coupler,
]


def test_all_organs_export_the_three_invariants():
    for organ in ORGANS:
        assert callable(getattr(organ, "coherence_vitals", None)), organ.__name__
        assert callable(getattr(organ, "handler", None)), organ.__name__
        assert callable(getattr(organ, "resonates_with", None)), organ.__name__


def test_all_organs_handler_returns_dict():
    for organ in ORGANS:
        out = organ.handler({})
        assert isinstance(out, dict), organ.__name__
        assert "error" not in out, (organ.__name__, out)


def test_orbit_cohesion_field_census():
    out = orbit_cohesion_field.handler({"action": "fleets"})
    fleets = out["fleets"]
    assert {f["fleet"] for f in fleets} == {"STARLINK", "ONEWEB", "IXP-SENTINEL"}
    assert sum(f["count"] for f in fleets) == out["total_objects"]


def test_orbit_cohesion_field_pair():
    out = orbit_cohesion_field.handler({"action": "pair", "a": "STLK-1", "b": "ONEW-1"})
    assert out["assessment"]["risk_level"] in ("green", "amber", "yellow", "red", "critical")


def test_decay_forecast_is_physical():
    out = decay_forecaster.handler({})
    assert out["days_to_reentry"] > 0
    assert out["orbits_remaining"] > 0
    assert out["input"]["altitude_km"] == 550.0


def test_anomaly_oracle_finds_something():
    out = telemetry_anomaly_oracle.handler({"mode": "demo"})
    verdicts = [v["verdict"] for k, v in out.items() if isinstance(v, dict) and "verdict" in v]
    assert verdicts, "oracle returned no verdicts"
    assert any(v != "clean" for v in verdicts)


def test_ground_station_passes():
    out = ground_station_synthesizer.handler({"lat": -33.86, "lon": 151.21, "fleet": "IXP-SENTINEL"})
    assert out["passes_computed"] > 0
    assert out["next_passes"]
    assert out["next_passes"][0]["countdown_s"] >= 0


def test_storyteller_tells():
    out = orbital_storyteller.handler({"kind": "conjunction"})
    assert "story" in out["entry"]
    assert out["entry"]["seal"] == "grazed"


def test_debris_census_and_breakup():
    census = debris_field_mapper.handler({})
    assert census["total_tracked_fragments"] > 1000
    event = debris_field_mapper.handler({"action": "breakup"})
    assert event["event"]["fragments"] > 0


def test_solar_coupling_storm_stronger_than_quiet():
    storm = solar_weather_coupler.handler({"kp": 8.0, "shell_km": 550.0})
    quiet = solar_weather_coupler.handler({"kp": 1.7, "shell_km": 550.0})
    assert storm["drag_multiplier"] > quiet["drag_multiplier"]
    assert storm["telemetry_impact"]["battery_derate_pct"] > quiet["telemetry_impact"]["battery_derate_pct"]


def test_noise_filter_removes_spikes():
    out = noise_filter.handler({"signal": [38.0 + (i % 3) * 0.5 for i in range(60)] + [98.0, 12.0]})
    assert out["outliers_removed"] >= 2
    assert max(out["cleaned_signal"]) < 60.0


def test_vitals_shape():
    for organ in ORGANS:
        vitals = organ.coherence_vitals()
        assert isinstance(vitals, dict), organ.__name__
        assert vitals.get("status") in ("resonant", "drifting", "fracturing",
                                        "stable", "thriving", "fragile"), organ.__name__
        assert vitals.get("wave") is not None, organ.__name__
        numeric = {k: v for k, v in vitals.items()
                   if isinstance(v, (int, float)) and k not in ("layer", "status", "wave")}
        assert numeric, f"{organ.__name__} reports no numeric vitals"
