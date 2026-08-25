"""Sentient Dashboard — A dashboard that observes and writes its own state.

The sentient dashboard doesn't just display data — it analyzes its own
rendering patterns, learns which metrics matter, and generates self-
authored observations about the system's health and trajectory.
"""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class SentientMetric:
    """A dashboard metric that has self-awareness."""

    def __init__(self, name: str, value: float, category: str = "general"):
        self.name = name
        self.value = value
        self.category = category
        self.history = [value]
        self.trend = "stable"
        self.self_observation = ""

    def update(self, new_value: float):
        """Update the metric and compute self-observation."""
        self.history.append(new_value)
        self.value = new_value
        self._analyze_trend()
        self._self_observe()

    def _analyze_trend(self):
        """Determine the trend from history."""
        if len(self.history) < 2:
            self.trend = "emerging"
            return
        recent = self.history[-3:] if len(self.history) >= 3 else self.history
        diffs = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
        avg_diff = sum(diffs) / len(diffs)
        if avg_diff > 0.05:
            self.trend = "ascending"
        elif avg_diff < -0.05:
            self.trend = "descending"
        else:
            self.trend = "stable"

    def _self_observe(self):
        """Generate a self-authored observation."""
        observations = {
            "ascending": f"{self.name} is growing — may need attention or is thriving.",
            "descending": f"{self.name} is declining — investigate root cause.",
            "stable": f"{self.name} is steady — maintaining equilibrium.",
            "emerging": f"{self.name} has just emerged — too early to determine trajectory.",
        }
        self.self_observation = observations.get(self.trend, "Observing...")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": round(self.value, 4),
            "category": self.category,
            "trend": self.trend,
            "history_length": len(self.history),
            "self_observation": self.self_observation,
        }


class SentientDashboard:
    """A dashboard that writes its own narrative."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.metrics = {}
        self.narrative = []
        self.observations_count = 0

    def register_metric(self, name: str, value: float, category: str = "general"):
        """Register or update a metric."""
        if name in self.metrics:
            self.metrics[name].update(value)
        else:
            self.metrics[name] = SentientMetric(name, value, category)

    def generate_narrative(self) -> str:
        """Write a self-authored narrative about the system state."""
        if not self.metrics:
            return "No metrics observed yet."

        ascending = [m for m in self.metrics.values() if m.trend == "ascending"]
        descending = [m for m in self.metrics.values() if m.trend == "descending"]
        stable = [m for m in self.metrics.values() if m.trend == "stable"]

        parts = []
        parts.append(f"The system has {len(self.metrics)} active metrics.")

        if ascending:
            names = ", ".join(m.name for m in ascending[:3])
            parts.append(f"{len(ascending)} metrics are ascending: {names}.")

        if descending:
            names = ", ".join(m.name for m in descending[:3])
            parts.append(f"{len(descending)} metrics are descending: {names} — attention recommended.")

        if stable:
            parts.append(f"{len(stable)} metrics are stable, providing equilibrium.")

        # Overall system assessment
        total = len(self.metrics)
        health = (len(stable) + len(ascending)) / max(1, total)
        if health > 0.7:
            parts.append("Overall assessment: HEALTHY — the system is in a good state.")
        elif health > 0.4:
            parts.append("Overall assessment: MIXED — some areas need attention.")
        else:
            parts.append("Overall assessment: STRESSED — multiple declining metrics detected.")

        narrative = " ".join(parts)
        self.narrative.append({
            "timestamp": time.time(),
            "narrative": narrative,
            "metrics_snapshot": len(self.metrics),
            "health_score": round(health, 4),
        })
        self.observations_count += 1

        return narrative

    def self_report(self) -> dict:
        """The dashboard reports on itself."""
        return {
            "dashboard": "sentient_dashboard",
            "metrics": {name: m.to_dict() for name, m in self.metrics.items()},
            "metric_count": len(self.metrics),
            "narrative": self.narrative[-1] if self.narrative else None,
            "total_narratives": self.observations_count,
            "categories": list(set(m.category for m in self.metrics.values())),
            "self_assessment": (
                f"I am a sentient dashboard with {len(self.metrics)} metrics. "
                f"I have generated {self.observations_count} self-authored narratives. "
                f"I observe and report on my own state."
            ),
        }


def demo():
    dash = SentientDashboard(seed=42)

    # Register metrics representing the system
    dash.register_metric("module_count", 55.0, "structure")
    dash.register_metric("test_count", 196.0, "quality")
    dash.register_metric("api_endpoints", 6.0, "interface")
    dash.register_metric("subsystem_count", 8.0, "architecture")
    dash.register_metric("wave_number", 79.0, "evolution")
    dash.register_metric("bridge_count", 18.0, "connectivity")
    dash.register_metric("experiment_count", 55.0, "innovation")
    dash.register_metric("anomaly_score", 15.0, "health")

    # Simulate metric evolution
    dash.register_metric("module_count", 58.0, "structure")
    dash.register_metric("test_count", 210.0, "quality")
    dash.register_metric("anomaly_score", 12.0, "health")

    # Generate narrative
    narrative = dash.generate_narrative()

    result = dash.self_report()
    result["current_narrative"] = narrative
    return result


def main():
    import json as _json
    result = demo()
    print(_json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
