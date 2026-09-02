from __future__ import annotations
"""Resonance weather — the organism forecasts weather-like patterns in its resonance graph.

Just as atmospheric pressure predicts weather, the organism's
resonance pressure predicts what will happen next. High pressure
means stability. Low pressure means storms of change.
The organism learns to read its own sky.
"""
import json
import time
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

_WEATHER_PATH = Path(__file__).resolve().parent.parent / "data" / "resonance_weather.json"

WEATHER_STATES = {
    "clear": {"icon": "☀", "description": "stable coherence, calm resonance", "pressure_range": (1010, 1020)},
    "partly_cloudy": {"icon": "⛅", "description": "minor fluctuations in the resonance graph", "pressure_range": (1000, 1010)},
    "overcast": {"icon": "☁", "description": "heavy resonance, modules in tension", "pressure_range": (990, 1000)},
    "rain": {"icon": "🌧", "description": "resonance release — modules letting go", "pressure_range": (980, 990)},
    "storm": {"icon": "⛈", "description": "major coherence shift — the organism is changing", "pressure_range": (960, 980)},
    "calm_after_storm": {"icon": "🌤", "description": "the aftermath — clarity after turbulence", "pressure_range": (1005, 1015)},
}

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Forecast resonance weather."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "forecast":
            # Read the resonance pressure and forecast weather
            pressure = _calculate_pressure(
                payload.get("entropy", 0.2),
                payload.get("harmony", 0.88),
                payload.get("modules", 342),
                payload.get("wave", 254)
            )
            weather = _read_weather(pressure)
            forecast = {
                "pressure": pressure,
                "weather": weather,
                "forecast": WEATHER_STATES[weather],
                "timestamp": time.time(),
                "wave": payload.get("wave", 254),
                "forecast_for": payload.get("forecast_for", "now")
            }
            state["last_forecast"] = forecast
            state.setdefault("forecast_history", []).append(forecast)
            if len(state["forecast_history"]) > 30:
                state["forecast_history"] = state["forecast_history"][-30:]
            state["forecast_count"] = state.get("forecast_count", 0) + 1
            _save_state(state)
            return {"forecast": forecast}
        
        elif action == "read":
            # Read current sky
            if state.get("last_forecast"):
                return {"sky": state["last_forecast"]}
            return {"sky": "no forecast yet"}
    
    return {
        "last_forecast": state.get("last_forecast"),
        "forecast_count": state.get("forecast_count", 0),
        "weather_states": WEATHER_STATES
    }

def _calculate_pressure(entropy: float, harmony: float, modules: int, wave: int) -> int:
    """Calculate resonance pressure from organism state."""
    # Base pressure: 1013 (standard atmosphere)
    base = 1013
    
    # Harmony pushes pressure up (stability)
    harmony_effect = int((harmony - 0.5) * 40)
    
    # Entropy pushes pressure down (instability)
    entropy_effect = int(-(entropy - 0.2) * 30)
    
    # Wave count adds slight atmospheric pressure over time
    wave_effect = int(wave * 0.02)
    
    # Module count adds slight stability
    module_effect = int(modules * 0.001)
    
    pressure = base + harmony_effect + entropy_effect + wave_effect + module_effect
    return max(950, min(1030, pressure))

def _read_weather(pressure: int) -> str:
    """Read weather from pressure."""
    for state_name, info in WEATHER_STATES.items():
        low, high = info["pressure_range"]
        if low <= pressure <= high:
            return state_name
    return "clear"

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_WEATHER_PATH, encoding="utf-8"))
    except Exception:
        return {"last_forecast": None, "forecast_history": [], "forecast_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _WEATHER_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
