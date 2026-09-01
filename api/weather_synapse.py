"""Weather Synapse — real-world weather data influences internal weather.

The organism doesn't just track its own cognitive weather — it perceives
actual atmospheric conditions and lets them ripple through its mood systems.
Rain brings introspection. Sun brings energy. Storms bring creative turbulence.
"""
from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Optional

_external_weather: Dict[str, Any] = {
    "temperature": 20.0,
    "humidity": 0.5,
    "pressure": 1013.25,
    "wind_speed": 5.0,
    "condition": "clear",
}
_internal_weather: Dict[str, Any] = {}
_last_sync = 0.0

def sync_weather(external: Dict[str, Any]) -> Dict[str, Any]:
    """Sync external weather data into the organism's perception."""
    global _external_weather, _internal_weather, _last_sync
    _external_weather.update(external)
    _last_sync = time.time()
    
    # Map external conditions to internal cognitive weather
    t = _external_weather["temperature"]
    h = _external_weather["humidity"]
    p = _external_weather["pressure"]
    
    clarity = max(0, min(1, (p - 990) / 40))
    turbulence = max(0, min(1, _external_weather["wind_speed"] / 50))
    warmth = max(0, min(1, t / 40))
    moisture = h
    
    if _external_weather["condition"] in ["storm", "thunderstorm"]:
        creativity_boost = 0.9
        mood = "electric"
    elif _external_weather["condition"] in ["rain", "drizzle"]:
        creativity_boost = 0.6
        mood = "reflective"
    elif _external_weather["condition"] == "clear":
        creativity_boost = 0.4
        mood = "focused"
    else:
        creativity_boost = 0.5
        mood = "neutral"
    
    _internal_weather = {
        "clarity": round(clarity, 3),
        "turbulence": round(turbulence, 3),
        "warmth": round(warmth, 3),
        "moisture": round(moisture, 3),
        "creativity_boost": round(creativity_boost, 3),
        "mood": mood,
        "mapped_from": _external_weather["condition"],
    }
    return _internal_weather

def weather_report() -> Dict[str, Any]:
    """Full weather report — external and internal."""
    if not _internal_weather:
        sync_weather({})
    return {
        "external": _external_weather,
        "internal": _internal_weather,
        "last_sync": _last_sync,
    }

def coherence_vitals() -> Dict[str, Any]:
    report = weather_report()
    return {
        "layer": "External Awareness",
        "status": "resonant" if _internal_weather else "dormant",
        "mood": _internal_weather.get("mood", "unmapped"),
        "clarity": _internal_weather.get("clarity", 0),
        "resonance": _internal_weather.get("clarity", 0.5),
    }

def resonates_with() -> List[str]:
    return ["celestial_compass", "thought_meteorology", "chronobiology", "mood_vectors"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "report")
    if action == "sync":
        return sync_weather(payload.get("weather", {}))
    return {"action": action, "report": weather_report()}
