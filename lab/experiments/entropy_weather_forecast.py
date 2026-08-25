from __future__ import annotations
"""Entropy Weather Forecast — predicts future system entropy states.

Like a meteorological system that predicts weather, this module tracks
entropy patterns across the system and forecasts future entropy states.
It classifies entropy into "weather" types (calm, storm, hurricane,
drought, monsoon) and provides confidence-weighted predictions.
"""
import math
import random
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from enum import Enum

class EntropyWeather(Enum):
    CALM = "calm"            # Low, stable entropy
    BREEZY = "breezy"        # Mild, fluctuating entropy
    STORM = "storm"          # High, volatile entropy
    HURRICANE = "hurricane"  # Extreme entropy
    DROUGHT = "drought"      # Very low entropy, stagnation
    MONSOON = "monsoon"      # Rapidly oscillating entropy

@dataclass
class EntropyReading:
    timestamp: float
    value: float
    weather: EntropyWeather
    volatility: float = 0.0
    trend: float = 0.0

@dataclass
class Forecast:
    horizon: int
    predicted_weather: EntropyWeather
    predicted_value: float
    confidence: float
    trend: str
    alerts: List[str] = field(default_factory=list)

class EntropyWeatherForecast:
    THRESHOLDS = {
        EntropyWeather.DROUGHT: (0.0, 0.15),
        EntropyWeather.CALM: (0.15, 0.35),
        EntropyWeather.BREEZY: (0.35, 0.55),
        EntropyWeather.STORM: (0.55, 0.75),
        EntropyWeather.HURRICANE: (0.75, 1.01),
    }

    def __init__(self, history_size: int = 50, seed: int = 42):
        self.history_size = history_size
        self.rng = random.Random(seed)
        self.readings: List[EntropyReading] = []
        self.forecasts: List[Forecast] = []

    def _classify(self, value: float) -> EntropyWeather:
        for weather, (low, high) in self.THRESHOLDS.items():
            if low <= value < high:
                return weather
        return EntropyWeather.HURRICANE

    def _volatility(self, recent_values: List[float]) -> float:
        if len(recent_values) < 2:
            return 0.0
        deltas = [abs(recent_values[i] - recent_values[i-1])
                  for i in range(1, len(recent_values))]
        return sum(deltas) / len(deltas)

    def _trend(self, recent_values: List[float]) -> float:
        if len(recent_values) < 3:
            return 0.0
        n = len(recent_values)
        first_half = sum(recent_values[:n//2]) / (n//2)
        second_half = sum(recent_values[n//2:]) / (n - n//2)
        return second_half - first_half

    def record(self, entropy_value: float) -> EntropyReading:
        recent = [r.value for r in self.readings[-10:]]
        recent.append(entropy_value)
        vol = self._volatility(recent)
        trend = self._trend(recent)
        weather = self._classify(entropy_value)

        if vol > 0.15 and weather in (EntropyWeather.STORM, EntropyWeather.HURRICANE):
            weather = EntropyWeather.MONSOON

        reading = EntropyReading(
            timestamp=len(self.readings),
            value=entropy_value,
            weather=weather,
            volatility=vol,
            trend=trend,
        )
        self.readings.append(reading)
        if len(self.readings) > self.history_size:
            self.readings.pop(0)
        return reading

    def forecast(self, horizon: int = 5) -> Forecast:
        if len(self.readings) < 5:
            return Forecast(
                horizon=horizon, predicted_weather=EntropyWeather.CALM,
                predicted_value=0.5, confidence=0.1, trend="insufficient_data"
            )

        recent = [r.value for r in self.readings[-10:]]
        current = recent[-1]
        trend = self._trend(recent)
        vol = self._volatility(recent)

        predicted_value = current + trend * horizon * 0.3
        predicted_value += self.rng.gauss(0, vol * 0.2)
        predicted_value = max(0.0, min(1.0, predicted_value))

        confidence = max(0.1, 1.0 - vol * 2 - abs(trend) * 3)
        confidence = min(1.0, confidence)

        predicted_weather = self._classify(predicted_value)

        trend_str = "rising" if trend > 0.02 else ("falling" if trend < -0.02 else "stable")

        alerts = []
        if predicted_weather == EntropyWeather.HURRICANE:
            alerts.append("WARNING: Hurricane entropy predicted")
        if vol > 0.2:
            alerts.append("ALERT: High volatility detected")
        if trend < -0.1:
            alerts.append("NOTICE: Entropy approaching drought")

        forecast = Forecast(
            horizon=horizon, predicted_weather=predicted_weather,
            predicted_value=round(predicted_value, 4),
            confidence=round(confidence, 3), trend=trend_str,
            alerts=alerts,
        )
        self.forecasts.append(forecast)
        return forecast

    def weather_history(self) -> List[Dict]:
        return [
            {"timestamp": r.timestamp, "value": round(r.value, 4),
             "weather": r.weather.value, "volatility": round(r.volatility, 4)}
            for r in self.readings
        ]

    def summary(self) -> Dict:
        if not self.readings:
            return {"readings": 0}
        weather_counts = {}
        for r in self.readings:
            weather_counts[r.weather.value] = weather_counts.get(r.weather.value, 0) + 1
        return {
            "total_readings": len(self.readings),
            "current_weather": self.readings[-1].weather.value,
            "current_value": round(self.readings[-1].value, 4),
            "weather_distribution": weather_counts,
            "avg_volatility": round(
                sum(r.volatility for r in self.readings) / len(self.readings), 4
            ),
            "forecasts_made": len(self.forecasts),
        }


def demo():
    forecaster = EntropyWeatherForecast(history_size=50, seed=42)
    print("=== Entropy Weather Forecast ===")

    patterns = (
        [0.1 + i * 0.02 for i in range(10)] +
        [0.3 + self_val * 0.05 for self_val in range(10)] +
        [0.8 - i * 0.03 for i in range(10)] +
        [0.2 + (i % 3) * 0.25 for i in range(10)]
    ) if False else None

    values = [0.1, 0.15, 0.2, 0.3, 0.35, 0.4, 0.5, 0.6, 0.7, 0.75,
              0.8, 0.85, 0.9, 0.85, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3,
              0.2, 0.15, 0.1, 0.15, 0.3, 0.5, 0.7, 0.9, 0.7, 0.5,
              0.3, 0.2, 0.15, 0.1, 0.2, 0.4, 0.6, 0.8, 0.6, 0.4]

    for v in values:
        forecaster.record(v)

    print(f"  Recorded {len(forecaster.readings)} entropy readings")

    forecast = forecaster.forecast(horizon=5)
    print(f"\n  5-step forecast:")
    print(f"    Weather: {forecast.predicted_weather.value}")
    print(f"    Value: {forecast.predicted_value}")
    print(f"    Confidence: {forecast.confidence}")
    print(f"    Trend: {forecast.trend}")
    if forecast.alerts:
        for alert in forecast.alerts:
            print(f"    Alert: {alert}")

    summary = forecaster.summary()
    print(f"\n  Summary:")
    print(f"    Current: {summary['current_weather']} ({summary['current_value']})")
    print(f"    Distribution: {summary['weather_distribution']}")
    print(f"    Avg volatility: {summary['avg_volatility']}")

    return summary


if __name__ == "__main__":
    demo()
