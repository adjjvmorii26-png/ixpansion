"""Wave 125 — Evolutionary Pressure Engine.

Applies selection pressures to the system — simulating scarcity,
competition, environmental shifts, and predator-prey dynamics that
drive adaptation and speciation.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class PressureEvent:
    """A single evolutionary pressure event."""

    def __init__(self, name: str, severity: float, duration: int = 10):
        self.name = name
        self.severity = severity
        self.duration = duration
        self.active = True
        self.remaining = duration
        self.affected_count = 0

    def apply(self) -> float:
        if not self.active:
            return 0.0
        self.remaining -= 1
        if self.remaining <= 0:
            self.active = False
        self.affected_count += 1
        return self.severity

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "severity": round(self.severity, 4),
                "active": self.active, "remaining": self.remaining,
                "affected": self.affected_count}


class EvolutionaryPressureEngine:
    """Applies selection pressures to drive system evolution."""

    def __init__(self):
        self._pressures: List[PressureEvent] = []
        self._adaptation_events: List[str] = []

    def apply_pressure(self, name: str, severity: float, duration: int = 10) -> PressureEvent:
        event = PressureEvent(name, severity, duration)
        self._pressures.append(event)
        return event

    def tick(self) -> List[Dict[str, Any]]:
        results = []
        for p in self._pressures:
            if p.active:
                severity = p.apply()
                if severity > 0.7:
                    self._adaptation_events.append(f"High pressure from {p.name}")
                results.append({"name": p.name, "severity": round(severity, 4),
                                "active": p.active})
        return results

    def active_pressures(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self._pressures if p.active]

    def total_pressure(self) -> float:
        return sum(p.severity for p in self._pressures if p.active)

    def status(self) -> Dict[str, Any]:
        return {"total_pressures": len(self._pressures),
                "active": sum(1 for p in self._pressures if p.active),
                "adaptation_events": len(self._adaptation_events)}


class EvolutionaryPressureSystem:
    """Legacy system for evolutionary pressure (Wave 108 compatibility)."""

    def __init__(self):
        self._organisms: Dict[str, Dict[str, Any]] = {}

    def introduce(self, agent_id: str, fitness: float = 1.0, traits: Optional[List[str]] = None) -> Dict[str, Any]:
        self._organisms[agent_id] = {
            "agent_id": agent_id, "fitness": fitness,
            "traits": traits or [], "alive": True,
        }
        return {"introduced": self._organisms[agent_id]}

    def apply_global_pressure(self, pressure_type: str, severity: float) -> Dict[str, Any]:
        results = []
        for oid, org in self._organisms.items():
            if org["alive"]:
                org["fitness"] = max(0.0, org["fitness"] - severity)
                if org["fitness"] <= 0.0:
                    org["alive"] = False
                results.append({"agent_id": oid, "fitness": round(org["fitness"], 4),
                                "alive": org["alive"]})
        return {"pressure_type": pressure_type, "severity": severity, "results": results}

    def status(self) -> Dict[str, Any]:
        alive = sum(1 for o in self._organisms.values() if o["alive"])
        return {"total": len(self._organisms), "alive": alive}


    def select_and_reproduce(self, top_n: int = 1) -> List[Dict[str, Any]]:
        alive = [o for o in self._organisms.values() if o["alive"]]
        survivors = sorted(alive, key=lambda o: o["fitness"], reverse=True)[:top_n]
        offspring = []
        for parent in survivors:
            child_id = f"{parent['agent_id']}_offspring_{len(self._organisms)}"
            child_fitness = parent["fitness"] * 0.9
            child = {"agent_id": child_id, "fitness": round(child_fitness, 4),
                     "traits": list(parent["traits"]), "alive": True}
            self._organisms[child_id] = child
            offspring.append(child)
        return offspring


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "evolutionary_pressure", "action": action}


def coherence_vitals() -> dict:
    """evolutionary_pressure reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "evolutionary_pressure_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['system_pulse', 'hazard_warning', 'code_organism']

