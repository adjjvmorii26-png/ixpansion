"""Wave 137 — Stress Simulator.

Subjects the civilization to synthetic shocks — spike load, worker
absence, economic crash — to measure how subsystems respond. Each
simulation grades the civilization's endurance and uncovers the
weakest link in a controlled, safe environment.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

SCENARIOS = ["spike_load", "worker_absence", "economic_crash", "network_outage", "supply_shock"]


class StressScenario:
    """A synthetic shock applied to the civilization."""

    def __init__(self, name: str, severity: float):
        self.name = name if name in SCENARIOS else "custom"
        self.severity = max(0.0, min(1.0, severity))
        self.results: List[float] = []
        self.created = time.time()
        self.id = hashlib.sha256(f"stress:{name}".encode()).hexdigest()[:10]

    def run(self, baseline_resilience: float) -> float:
        degraded = baseline_resilience * (1.0 - self.severity)
        self.results.append(degraded)
        return round(degraded, 4)

    def worst_case(self) -> float:
        return min(self.results) if self.results else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "severity": self.severity,
                "worst_case": self.worst_case()}


class StressSimulator:
    """Runs resilience stress scenarios."""

    def __init__(self):
        self._scenarios: Dict[str, StressScenario] = {}
        self._runs = 0

    def scenario(self, name: str, severity: float) -> StressScenario:
        scenario = StressScenario(name, severity)
        self._scenarios[scenario.id] = scenario
        return scenario

    def execute(self, scenario_id: str, baseline_resilience: float) -> float:
        scenario = self._scenarios.get(scenario_id)
        if scenario is None:
            return 0.0
        self._runs += 1
        return scenario.run(baseline_resilience)

    def weakest(self) -> str:
        if not self._scenarios:
            return "none"
        return min(self._scenarios, key=lambda s: self._scenarios[s].worst_case())

    def status(self) -> Dict[str, Any]:
        return {"scenarios": len(self._scenarios), "runs": self._runs,
                "weakest_scenario": self.weakest()}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    simulator = StressSimulator()
    return {"status": "active", "module": "stress_simulator",
            **simulator.status()}
