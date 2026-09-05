"""Emotion Weather — tracks the emotional climate across the agent ecosystem.

Like meteorological weather, emotional weather has fronts, pressure systems,
and seasonal patterns. High-pressure zones indicate emotional stability;
low-pressure zones indicate emotional turbulence. Fronts passing through
can trigger mass emotional shifts.
"""
from __future__ import annotations

import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class EmotionalZone:
    def __init__(self, name: str):
        self.name = name
        self.valence = random.uniform(-0.5, 0.5)
        self.arousal = random.uniform(0.3, 0.7)
        self.pressure = 50.0 + random.uniform(-10, 10)
        self.history: List[Dict[str, float]] = []

    def shift(self, valence_delta: float, arousal_delta: float):
        self.valence = max(-1.0, min(1.0, self.valence + valence_delta))
        self.arousal = max(0.0, min(1.0, self.arousal + arousal_delta))
        self.pressure += valence_delta * 10
        self.pressure = max(0, min(100, self.pressure))
        self.history.append({"v": self.valence, "a": self.arousal, "p": self.pressure})
        if len(self.history) > 50:
            self.history = self.history[-50:]

    def weather_type(self) -> str:
        if self.valence > 0.3 and self.arousal < 0.4:
            return "serene"
        elif self.valence > 0.3 and self.arousal > 0.5:
            return "exuberant"
        elif self.valence < -0.3 and self.arousal > 0.5:
            return "stormy"
        elif self.valence < -0.3:
            return "melancholy"
        elif self.pressure < 30:
            return "volatile"
        return "calm"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "valence": round(self.valence, 3),
            "arousal": round(self.arousal, 3),
            "pressure": round(self.pressure, 1),
            "weather": self.weather_type(),
        }


class EmotionWeatherSystem:
    def __init__(self):
        self.zones: Dict[str, EmotionalZone] = {}
        self.fronts: List[Dict[str, Any]] = []
        self.tick_count = 0

    def register_zone(self, name: str) -> Dict[str, Any]:
        self.zones[name] = EmotionalZone(name)
        return {"zone": self.zones[name].to_dict()}

    def shift_zone(self, name: str, valence_delta: float, arousal_delta: float) -> Dict[str, Any]:
        if name not in self.zones:
            return {"error": "zone not found"}
        self.zones[name].shift(valence_delta, arousal_delta)
        return self.zones[name].to_dict()

    def weather_front(self, from_zone: str, to_zone: str, intensity: float = 0.3) -> Dict[str, Any]:
        if from_zone not in self.zones or to_zone not in self.zones:
            return {"error": "zone not found"}
        source = self.zones[from_zone]
        target = self.zones[to_zone]
        target.shift(source.valence * intensity, source.arousal * intensity * 0.5)
        front = {
            "from": from_zone, "to": to_zone,
            "intensity": intensity, "time": time.time(),
        }
        self.fronts.append(front)
        return {"front": front, "target_weather": target.weather_type()}

    def tick(self) -> Dict[str, Any]:
        self.tick_count += 1
        for zone in self.zones.values():
            zone.shift(random.uniform(-0.02, 0.02), random.uniform(-0.01, 0.01))
        return {"tick": self.tick_count, "zones": {k: z.weather_type() for k, z in self.zones.items()}}

    def full_map(self) -> List[Dict[str, Any]]:
        return [z.to_dict() for z in self.zones.values()]

    def system_stats(self) -> Dict[str, Any]:
        weather_counts: Dict[str, int] = {}
        for z in self.zones.values():
            w = z.weather_type()
            weather_counts[w] = weather_counts.get(w, 0) + 1
        return {
            "total_zones": len(self.zones),
            "total_fronts": len(self.fronts),
            "weather_distribution": weather_counts,
            "ticks": self.tick_count,
        }


_weather = EmotionWeatherSystem()


def emotion_weather_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "register":
        return _weather.register_zone(payload.get("name", f"zone_{random.randint(100,999)}"))
    elif action == "shift":
        return _weather.shift_zone(
            payload.get("zone", ""), payload.get("valence_delta", 0.0), payload.get("arousal_delta", 0.0),
        )
    elif action == "front":
        return _weather.weather_front(
            payload.get("from", ""), payload.get("to", ""), payload.get("intensity", 0.3),
        )
    elif action == "tick":
        return _weather.tick()
    elif action == "map":
        return {"zones": _weather.full_map()}
    return {"status": "active", **_weather.system_stats()}


handler = emotion_weather_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "0", "module": "emotion_weather"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "emotion_weather", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
