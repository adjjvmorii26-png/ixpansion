"""Entropy Weather — Forecasts codebase entropy patterns like a weather system.

Models code complexity, duplication, and decay as atmospheric phenomena.
Generates "weather reports" with fronts, pressure systems, and forecasts.
"""
from __future__ import annotations
import hashlib
import math
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class WeatherFront:
    """An entropy front moving through the codebase."""

    def __init__(self, name: str, intensity: float, direction: str):
        self.name = name
        self.intensity = intensity
        self.direction = direction
        self.speed = intensity * 0.5

    def advance(self, time_step: float = 1.0) -> float:
        return self.intensity * math.exp(-self.speed * time_step * 0.1)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "intensity": round(self.intensity, 4),
            "direction": self.direction,
            "speed": round(self.speed, 4),
        }


class EntropyWeather:
    """Generates entropy weather forecasts for the codebase."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.pressure_systems = []
        self.fronts = []
        self.forecast = []

    def measure_pressure(self, subsystem: str, modules: int, total_lines: int) -> dict:
        """Compute entropy pressure for a subsystem."""
        # High lines per module = high pressure
        density = total_lines / max(1, modules)
        pressure = min(100.0, density / 10.0)

        # Temperature: inverse of module count (fewer modules = hotter)
        temperature = max(0.0, 50.0 - modules * 2)

        # Humidity: based on test coverage (fewer tests = more humid/unstable)
        humidity = max(0.0, min(100.0, 80.0 - modules * 3))

        system = {
            "subsystem": subsystem,
            "pressure": round(pressure, 2),
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "modules": modules,
            "total_lines": total_lines,
        }
        self.pressure_systems.append(system)
        return system

    def generate_fronts(self) -> list[WeatherFront]:
        """Generate weather fronts from pressure systems."""
        for i in range(len(self.pressure_systems) - 1):
            curr = self.pressure_systems[i]
            nxt = self.pressure_systems[i + 1]

            pressure_diff = nxt["pressure"] - curr["pressure"]
            if abs(pressure_diff) > 5:
                direction = "warm" if pressure_diff > 0 else "cold"
                front = WeatherFront(
                    name=f"{curr['subsystem']}→{nxt['subsystem']}",
                    intensity=abs(pressure_diff),
                    direction=direction,
                )
                self.fronts.append(front)

        return self.fronts

    def forecast_weather(self, steps: int = 5) -> list[dict]:
        """Forecast weather evolution over multiple time steps."""
        self.forecast = []

        for step in range(steps):
            step_data = {"time_step": step, "systems": []}
            for system in self.pressure_systems:
                # Pressure drifts toward equilibrium
                target = 50.0
                drift = (target - system["pressure"]) * 0.05
                new_pressure = system["pressure"] + drift + (hash(str(step + self.seed)) % 10 - 5) * 0.1
                new_pressure = max(0, min(100, new_pressure))

                # Classify weather
                if new_pressure > 75:
                    condition = "stormy"
                elif new_pressure > 50:
                    condition = "cloudy"
                elif new_pressure > 25:
                    condition = "partly_cloudy"
                else:
                    condition = "clear"

                step_data["systems"].append({
                    "subsystem": system["subsystem"],
                    "pressure": round(new_pressure, 2),
                    "condition": condition,
                })
            self.forecast.append(step_data)

        return self.forecast

    def generate_report(self) -> str:
        """Generate a human-readable weather report."""
        lines = ["═══ ENTROPY WEATHER REPORT ═══", ""]

        for system in self.pressure_systems:
            p = system["pressure"]
            if p > 75:
                emoji = "⛈"
            elif p > 50:
                emoji = "☁"
            elif p > 25:
                emoji = "⛅"
            else:
                emoji = "☀"
            lines.append(f"{emoji} {system['subsystem']}: {p:.1f} hPa | {system['temperature']:.0f}° | {system['humidity']:.0f}% humid")

        if self.fronts:
            lines.append("")
            lines.append("Fronts:")
            for f in self.fronts:
                lines.append(f"  {'→' if f.direction == 'warm' else '←'} {f.name} ({f.direction}, {f.intensity:.1f})")

        if self.forecast:
            lines.append("")
            lines.append(f"Forecast ({len(self.forecast)} steps):")
            for step in self.forecast[:3]:
                conditions = [s["condition"] for s in step["systems"]]
                lines.append(f"  t+{step['time_step']}: {', '.join(conditions)}")

        return "\n".join(lines)

    def report(self) -> dict:
        """Generate full entropy weather report."""
        self.generate_fronts()
        self.forecast_weather(steps=5)
        weather_text = self.generate_report()

        return {
            "weather": "entropy_weather",
            "pressure_systems": self.pressure_systems,
            "fronts": [f.to_dict() for f in self.fronts],
            "forecast_steps": len(self.forecast),
            "forecast": self.forecast,
            "report_text": weather_text,
            "signature": hashlib.md5(weather_text.encode()).hexdigest()[:12],
        }


def demo():
    weather = EntropyWeather(seed=42)

    # Measure pressure for each subsystem
    subsystems = {
        "api": (ROOT / "api", 9),
        "lab_experiments": (ROOT / "lab" / "experiments", 55),
        "bridges": (ROOT / "bridges", 18),
        "constellation": (ROOT / "constellation", 5),
        "mycelium": (ROOT / "mycelium", 3),
    }

    for name, (base, expected_modules) in subsystems.items():
        if base.exists():
            py_files = [f for f in base.glob("*.py") if not f.name.startswith("_") and not f.name.startswith("test_")]
            total_lines = sum(len(f.read_text(errors="replace").splitlines()) for f in py_files)
            weather.measure_pressure(name, len(py_files), total_lines)

    return weather.report()


def main():
    import json
    result = demo()
    print(result["report_text"])
    print("\n--- JSON ---")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
