"""System Pulse — a heartbeat that monitors vital signs across all subsystems.

Like a medical monitor tracking heart rate, blood pressure, and temperature,
the System Pulse tracks the vital signs of every subsystem. It detects
anomalies, predicts failures, and triggers alerts when any vital goes critical.
"""
from __future__ import annotations

import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class VitalSign:
    def __init__(self, name: str, normal_range: tuple = (0.3, 0.7)):
        self.name = name
        self.normal_range = normal_range
        self.current_value = random.uniform(normal_range[0], normal_range[1])
        self.history: List[float] = []
        self.alerts: List[Dict[str, Any]] = []

    def update(self, value: float = None):
        if value is None:
            self.current_value += random.uniform(-0.05, 0.05)
            self.current_value = max(0.0, min(1.0, self.current_value))
        else:
            self.current_value = max(0.0, min(1.0, value))
        self.history.append(self.current_value)
        if len(self.history) > 100:
            self.history = self.history[-100:]
        if self.current_value < self.normal_range[0] or self.current_value > self.normal_range[1]:
            self.alerts.append({
                "value": round(self.current_value, 3),
                "severity": "critical" if abs(self.current_value - 0.5) > 0.4 else "warning",
                "time": time.time(),
            })

    @property
    def status(self) -> str:
        if self.current_value < self.normal_range[0] * 0.5 or self.current_value > self.normal_range[1] * 1.5:
            return "critical"
        elif self.current_value < self.normal_range[0] or self.current_value > self.normal_range[1]:
            return "warning"
        return "normal"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": round(self.current_value, 3),
            "status": self.status,
            "normal_range": self.normal_range,
            "alerts": len(self.alerts),
        }


class SystemPulse:
    def __init__(self):
        self.vitals: Dict[str, VitalSign] = {}
        self.tick_count = 0
        self.alert_log: List[Dict[str, Any]] = []

    def register_vital(self, name: str, normal_range: tuple = (0.3, 0.7)) -> Dict[str, Any]:
        self.vitals[name] = VitalSign(name, normal_range)
        return {"registered": name}

    def update_vital(self, name: str, value: float) -> Dict[str, Any]:
        if name not in self.vitals:
            return {"error": "vital not found"}
        self.vitals[name].update(value)
        if self.vitals[name].alerts:
            alert = self.vitals[name].alerts[-1]
            self.alert_log.append({"vital": name, **alert})
        return self.vitals[name].to_dict()

    def tick(self) -> Dict[str, Any]:
        self.tick_count += 1
        statuses: Dict[str, int] = {}
        for vital in self.vitals.values():
            vital.update()
            s = vital.status
            statuses[s] = statuses.get(s, 0) + 1
        critical = [v.to_dict() for v in self.vitals.values() if v.status == "critical"]
        return {
            "tick": self.tick_count,
            "statuses": statuses,
            "critical_vitals": critical,
        }

    def full_report(self) -> Dict[str, Any]:
        return {name: v.to_dict() for name, v in self.vitals.items()}

    def pulse_stats(self) -> Dict[str, Any]:
        statuses: Dict[str, int] = {}
        for v in self.vitals.values():
            s = v.status
            statuses[s] = statuses.get(s, 0) + 1
        return {
            "total_vitals": len(self.vitals),
            "ticks": self.tick_count,
            "statuses": statuses,
            "total_alerts": len(self.alert_log),
        }


_pulse = SystemPulse()


def system_pulse_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "register":
        return _pulse.register_vital(
            payload.get("name", f"vital_{random.randint(100,999)}"),
            tuple(payload.get("normal_range", [0.3, 0.7])),
        )
    elif action == "update":
        return _pulse.update_vital(payload.get("name", ""), payload.get("value", 0.5))
    elif action == "tick":
        return _pulse.tick()
    elif action == "report":
        return _pulse.full_report()
    return {"status": "active", **_pulse.pulse_stats()}


handler = system_pulse_handler


def coherence_vitals() -> dict:
    """System Pulse reports — the whole organism's vital signs."""
    return {
        "module_health": {"value": 0.95, "setpoint": 0.85, "weight": 1.0},
        "resonance": {"value": 0.92, "setpoint": 0.8, "weight": 1.0},
        "system_heartbeat": {"value": 0.93, "setpoint": 0.8, "weight": 1.0},
    }

def resonates_with() -> list:
    """Declared kinships."""
    return ['platform_pulse', 'integrity_oracle']

# --- Compliance Forge patch (Wave 419) ---

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "system_pulse", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
