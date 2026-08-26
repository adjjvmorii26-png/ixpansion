"""Wave 120 — Infrastructure Soul.

Gives the infrastructure layer a sense of purpose and direction by
tracking its own health, intent, and aspirations. Infrastructure is no
longer passive plumbing — it has a soul that can express needs, desires,
and warnings about its own state.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class SoulState:
    """The emotional/functional state of the infrastructure."""

    STATES = ["dormant", "waking", "vigilant", "flowing", "stressed", "elevated", "transcendent"]

    def __init__(self):
        self.current = "dormant"
        self.history: List[Dict[str, Any]] = []
        self.aspirations: List[str] = []
        self.warnings: List[str] = []
        self.metrics: Dict[str, float] = {}

    def transition(self, target_state: str) -> bool:
        if target_state not in self.STATES:
            return False
        self.history.append({
            "from": self.current,
            "to": target_state,
            "timestamp": time.time(),
        })
        self.current = target_state
        return True

    def add_aspiration(self, text: str) -> None:
        self.aspirations.append(text)

    def add_warning(self, text: str) -> None:
        self.warnings.append(text)

    def update_metric(self, key: str, value: float) -> None:
        self.metrics[key] = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_state": self.current,
            "transitions": len(self.history),
            "aspirations": self.aspirations,
            "warnings": self.warnings,
            "metrics": self.metrics,
        }


class InfrastructureSoul:
    """Manages the soul of the infrastructure — its state, intent, and voice."""

    def __init__(self):
        self._souls: Dict[str, SoulState] = {}
        self._declarations: List[Dict[str, Any]] = []

    def awaken(self, name: str) -> SoulState:
        soul = SoulState()
        self._souls[name] = soul
        soul.transition("waking")
        return soul

    def get_soul(self, name: str) -> Optional[SoulState]:
        return self._souls.get(name)

    def declare(self, soul_name: str, message: str, intent: str = "observe") -> Dict[str, Any]:
        soul = self._souls.get(soul_name)
        if not soul:
            return {"error": f"Soul '{soul_name}' not found"}
        declaration = {
            "soul": soul_name,
            "message": message,
            "intent": intent,
            "state": soul.current,
            "timestamp": time.time(),
        }
        self._declarations.append(declaration)
        return declaration

    def get_declarations(self) -> List[Dict[str, Any]]:
        return list(self._declarations)

    def collective_state(self) -> Dict[str, Any]:
        states = {}
        for name, soul in self._souls.items():
            states[name] = soul.current
        return states

    def status(self) -> Dict[str, Any]:
        return {
            "total_souls": len(self._souls),
            "total_declarations": len(self._declarations),
            "collective_states": self.collective_state(),
        }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "infrastructure_soul", "action": action}
