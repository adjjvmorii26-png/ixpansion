"""Thought Meteorology — forecasts the weather of ideas across the frontier.

Watches the frontier's module ecosystem and reports the "weather" of thought:
which concepts are heating up (rapid module growth/connection), which are
cooling down, and what fronts are forming. Like weather, ideas have pressure
systems, fronts, and storms.

Usage:
  GET /api/thought_meteorology                      — current idea weather
  GET /api/thought_meteorology?forecast=3           — 3-period forecast
  POST /api/thought_meteorology {"region": "garden"} — focused reading
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]

WEATHER_STATES = ["clear", "partly-cloudy", "overcast", "storm-driving",
                  "fog-of-theory", "heat-wave", "cold-front", "supercell"]


def _module_names() -> List[str]:
    api_dir = ROOT / "api"
    return [p.stem for p in api_dir.glob("*.py")
            if p.stem not in ("__init__", "index", "unified_router")]


def _tokens(name: str) -> List[str]:
    return re.findall(r"[a-z]+", name.lower())


def _token_frequency(names: List[str]) -> Counter:
    freq = Counter()
    for name in names:
        seen = set()
        for tok in _tokens(name):
            if tok not in seen:
                freq[tok] += 1
                seen.add(tok)
    return freq


def _token_signal(tok: str, freq: Counter, total_modules: int) -> float:
    """Compute a normalized 'signal strength' for a concept token."""
    return freq.get(tok, 0) / max(total_modules, 1)


def _region_weather(region: str, names: List[str], freq: Counter) -> Dict[str, Any]:
    """Compute weather for a specific region (concept) of the frontier."""
    region_modules = [n for n in names if region in _tokens(n)]
    if not region_modules:
        return {
            "region": region,
            "state": "void",
            "modules": 0,
            "reading": f"No modules explicitly carry the concept '{region}'.",
        }

    # Compute pressure from module connectivity
    related = 0
    for name in region_modules:
        for tok in set(_tokens(name)):
            if tok != region:
                related += freq.get(tok, 0) - 1  # how many other modules share this token

    pressure = round(min(1.0, related / max(len(region_modules) * 5, 1)), 3)

    # Map pressure to weather
    if pressure < 0.2:
        state = "clear"
    elif pressure < 0.4:
        state = "partly-cloudy"
    elif pressure < 0.6:
        state = "overcast"
    elif pressure < 0.8:
        state = "storm-driving"
    else:
        state = "supercell"

    return {
        "region": region,
        "state": state,
        "pressure": pressure,
        "modules": len(region_modules),
        "reading": (
            f"The {region} concept sustains {len(region_modules)} modules "
            f"under {state} skies with pressure {pressure}."
        ),
    }


def forecast(periods: int = 3) -> Dict[str, Any]:
    """Generate a 3-period idea weather forecast."""
    names = _module_names()
    freq = _token_frequency(names)
    total = len(names)
    hottest = freq.most_common(10)
    hottest = [(t, round(_token_signal(t, freq, total), 3)) for t, _ in hottest]

    # Forecast: hottest concepts are predicted to keep heating (momentum)
    forecast_periods = []
    for p in range(1, periods + 1):
        forecast_periods.append({
            "period": p,
            "heating": [(t, round(min(1.0, s + p * 0.01), 3)) for t, s in hottest[:3]],
            "note": f"In {p} periods, the densest concept keeps growing — ideas feed on connections.",
        })

    return {
        "total_modules": total,
        "hottest_concepts": hottest,
        "forecast_periods": forecast_periods,
        "report": (
            f"The frontier's hottest concept is '{hottest[0][0]}' "
            f"(signal {hottest[0][1]}). The idea-weather is {WEATHER_STATES[3]} "
            "over the dense regions, with a cold front passing over isolated "
            "experiments."
        ),
    }


def full_weather() -> Dict[str, Any]:
    """Full 360-degree idea weather report."""
    names = _module_names()
    freq = _token_frequency(names)
    total = len(names)

    # Overall weather state
    top_signal = max([_token_signal(t, freq, total) for t, _ in freq.most_common(5)] + [0.0])
    if top_signal < 0.05:
        overall = "clear"
    elif top_signal < 0.10:
        overall = "partly-cloudy"
    elif top_signal < 0.18:
        overall = "overcast"
    else:
        overall = "heat-wave"

    # Top regions with weather
    regions = []
    for tok, _ in freq.most_common(20):
        w = _region_weather(tok, names, freq)
        regions.append(w)

    # Identify 'fronts' — tokens that bridge many other tokens (high connectivity)
    fronts = []
    for tok, count in freq.most_common(25):
        if count >= 3:
            fronts.append({"concept": tok, "module_count": count,
                           "role": "connector"})

    return {
        "frontier_name": "IXpansion",
        "overall_weather": overall,
        "pressure_centers": regions[:12],
        "storm_fronts": fronts[:8],
        "temperature_reading": (
            f"Signal temperature {round(top_signal * 100, 1)}° — "
            f"{'warming' if overall == 'heat-wave' else 'stable'}."
        ),
        "insurance_note": "Idea weather is a metaphor. The frontier is not actually storming.",
        "philosophy": (
            "Ideas move like weather. They build pressure, form fronts, and "
            "break into storms. Watch the dense regions — that's where the "
            "next supercell of thought is forming."
        ),
    }


def coherence_vitals() -> dict:
    """Thought Meteorology reports idea pressure."""
    from api.thought_meteorology import _module_names, _token_frequency
    names = _module_names()
    freq = _token_frequency(names)
    pressure = min(1.0, len(freq) / max(len(names), 1))
    return {"idea_pressure": pressure,
            "module_health": 0.88,
            "resonance": 0.8}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    region = payload.get("region")
    forecast_periods = int(payload.get("forecast", 0))

    if region:
        names = _module_names()
        freq = _token_frequency(names)
        result = _region_weather(region, names, freq)
        result["action"] = "region"
        return result
    if forecast_periods > 0:
        result = forecast(forecast_periods)
        result["action"] = "forecast"
        return result

    result = full_weather()
    result["action"] = "weather"
    return result
