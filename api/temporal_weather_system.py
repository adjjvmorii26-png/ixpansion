"""Wave 124 — Temporal Weather System.

Models temporal phenomena as weather — periods of calm, storms of rapid
change, fog of uncertainty, and lightning strikes of innovation. The
system can forecast and adapt to temporal weather patterns.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class WeatherPattern:
    """A temporal weather condition."""

    PATTERNS = ["calm", "breeze", "gale", "storm", "fog", "lightning", "blizzard", "rainbow"]

    def __init__(self, name: str, pattern: str, intensity: float = 0.5):
        self.name = name
        self.pattern = pattern if pattern in self.PATTERNS else "calm"
        self.intensity = intensity
        self.created = time.time()

    def evolve(self, delta: float) -> float:
        self.intensity = max(0.0, min(1.0, self.intensity + delta))
        return self.intensity

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "pattern": self.pattern,
                "intensity": round(self.intensity, 4)}


class TemporalWeatherSystem:
    """Forecasts and manages temporal weather."""

    def __init__(self):
        self._current: WeatherPattern = WeatherPattern("default", "calm", 0.3)
        self._history: List[Dict[str, Any]] = []
        self._forecasts: List[Dict[str, Any]] = []

    def observe(self) -> Dict[str, Any]:
        self._history.append(self._current.to_dict())
        return self._current.to_dict()

    def change_weather(self, pattern: str, intensity: float = 0.5) -> Dict[str, Any]:
        self._current = WeatherPattern(f"system_{len(self._history)}", pattern, intensity)
        result = self._current.to_dict()
        self._history.append(result)
        return result

    def forecast(self, steps: int = 3) -> List[Dict[str, Any]]:
        predictions = []
        current_intensity = self._current.intensity
        for i in range(steps):
            delta = (i % 3 - 1) * 0.1
            current_intensity = max(0.0, min(1.0, current_intensity + delta))
            predicted_pattern = "storm" if current_intensity > 0.7 else "calm" if current_intensity < 0.3 else "breeze"
            predictions.append({"step": i + 1, "pattern": predicted_pattern,
                                "intensity": round(current_intensity, 4)})
        self._forecasts.extend(predictions)
        return predictions

    def status(self) -> Dict[str, Any]:
        return {"current": self._current.pattern, "current_intensity": round(self._current.intensity, 4),
                "history_length": len(self._history), "forecasts": len(self._forecasts)}
