"""Semantic Weather — tracks the atmospheric conditions of meaning in the system.

The system has "weather" made of semantic pressure, ambiguity fog,
precision sunshine, contradiction storms, and metaphor rain. Agents
can check the forecast and adapt their communication style accordingly.
"""
from __future__ import annotations

import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

WEATHER_TYPES = {
    "clear": {"ambiguity": 0.1, "precision": 0.9, "contradiction": 0.0, "metaphor": 0.2},
    "foggy": {"ambiguity": 0.8, "precision": 0.3, "contradiction": 0.2, "metaphor": 0.5},
    "stormy": {"ambiguity": 0.5, "precision": 0.2, "contradiction": 0.9, "metaphor": 0.7},
    "rainy": {"ambiguity": 0.4, "precision": 0.5, "contradiction": 0.3, "metaphor": 0.8},
    "sunny": {"ambiguity": 0.2, "precision": 0.8, "contradiction": 0.1, "metaphor": 0.3},
    "blizzard": {"ambiguity": 0.9, "precision": 0.1, "contradiction": 0.8, "metaphor": 0.6},
    "aurora": {"ambiguity": 0.3, "precision": 0.7, "contradiction": 0.4, "metaphor": 0.9},
}


class SemanticWeatherSystem:
    def __init__(self):
        self.pressure = 50.0
        self.humidity = 50.0
        self.wind_speed = 10.0
        self.temperature = 20.0
        self.forecast: List[Dict[str, Any]] = []
        self.readings: List[Dict[str, Any]] = []
        self.current_type = "clear"

    def current_conditions(self) -> Dict[str, Any]:
        conditions = self._compute_conditions()
        self.current_type = conditions["weather_type"]
        return conditions

    def _compute_conditions(self) -> Dict[str, Any]:
        ambiguity = self.humidity / 100.0
        precision = max(0, 1.0 - ambiguity)
        contradiction = self.wind_speed / 100.0
        metaphor = self.temperature / 50.0

        best_type = "clear"
        best_score = float("inf")
        for wtype, params in WEATHER_TYPES.items():
            score = (
                abs(ambiguity - params["ambiguity"]) +
                abs(precision - params["precision"]) +
                abs(contradiction - params["contradiction"]) +
                abs(metaphor - params["metaphor"])
            )
            if score < best_score:
                best_score = score
                best_type = wtype

        return {
            "weather_type": best_type,
            "ambiguity": round(ambiguity, 3),
            "precision": round(precision, 3),
            "contradiction": round(contradiction, 3),
            "metaphor": round(metaphor, 3),
            "pressure": round(self.pressure, 1),
            "temperature": round(self.temperature, 1),
            "wind_speed": round(self.wind_speed, 1),
            "visibility": round(precision * 100, 1),
        }

    def inject_confusion(self, amount: float = 10.0) -> Dict[str, Any]:
        self.humidity = min(100, self.humidity + amount)
        self.pressure = max(0, self.pressure - amount / 2)
        return {"event": "confusion_front_moving_in", **self.current_conditions()}

    def inject_clarity(self, amount: float = 10.0) -> Dict[str, Any]:
        self.humidity = max(0, self.humidity - amount)
        self.pressure = min(100, self.pressure + amount / 2)
        return {"event": "clarity_breaking_through", **self.current_conditions()}

    def inject_storm(self, intensity: float = 20.0) -> Dict[str, Any]:
        self.wind_speed = min(100, self.wind_speed + intensity)
        self.temperature = max(-10, self.temperature - intensity / 4)
        return {"event": "contradiction_storm_approaching", **self.current_conditions()}

    def tick(self) -> Dict[str, Any]:
        """Natural drift of weather."""
        self.pressure += random.uniform(-2, 2)
        self.humidity += random.uniform(-3, 3)
        self.wind_speed += random.uniform(-1, 1)
        self.temperature += random.uniform(-0.5, 0.5)
        self.pressure = max(0, min(100, self.pressure))
        self.humidity = max(0, min(100, self.humidity))
        self.wind_speed = max(0, min(100, self.wind_speed))
        self.temperature = max(-20, min(50, self.temperature))
        conditions = self.current_conditions()
        self.readings.append(conditions)
        return conditions

    def forecast_next(self, hours: int = 3) -> List[Dict[str, Any]]:
        saved = (self.pressure, self.humidity, self.wind_speed, self.temperature)
        predictions = []
        for _ in range(hours):
            self.tick()
            predictions.append(self.current_conditions())
        self.pressure, self.humidity, self.wind_speed, self.temperature = saved
        self.forecast = predictions
        return predictions

    def advice_for_agents(self) -> Dict[str, Any]:
        conditions = self.current_conditions()
        weather = conditions["weather_type"]
        advice = {
            "clear": "Communicate precisely. Low metaphor load.",
            "foggy": "Reduce ambiguity. Use explicit statements.",
            "stormy": "Delay important decisions. Shield sensitive agents.",
            "rainy": "Use creative metaphors. Good time for brainstorming.",
            "sunny": "High-precision work. Execute plans.",
            "blizzard": "Emergency protocol. All agents should be conservative.",
            "aurora": "Inspiration peaks. Launch creative experiments.",
        }
        return {
            "current_weather": weather,
            "advice": advice.get(weather, "No specific advice."),
            "conditions": conditions,
        }


_weather = SemanticWeatherSystem()


def semantic_weather_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "conditions":
        return _weather.current_conditions()
    elif action == "inject_confusion":
        return _weather.inject_confusion(payload.get("amount", 10.0))
    elif action == "inject_clarity":
        return _weather.inject_clarity(payload.get("amount", 10.0))
    elif action == "inject_storm":
        return _weather.inject_storm(payload.get("intensity", 20.0))
    elif action == "tick":
        return _weather.tick()
    elif action == "forecast":
        return {"forecast": _weather.forecast_next(payload.get("hours", 3))}
    elif action == "advice":
        return _weather.advice_for_agents()
    return {"status": "active", **_weather.current_conditions()}


handler = semantic_weather_handler
