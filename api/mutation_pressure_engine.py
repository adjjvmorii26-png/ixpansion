"""Wave 406 — Mutation Pressure Engine.

The vault organs now drive mutation pressure across the organism.
When storage accumulates entropy, it generates pressure that
forces new module births, parameter shifts, and structural mutations.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional


class MutationPressureEngine:
    """Generates mutation pressure from vault entropy accumulation."""

    def __init__(self):
        self.pressure_history: List[Dict] = []
        self.current_pressure = 0.0
        self.max_pressure = 1.0
        self.mutation_events: List[Dict] = []

    def calculate_pressure(self, vault_state: Dict[str, Any]) -> float:
        """Compute mutation pressure from vault entropy metrics."""
        entropy = vault_state.get("entropy_score", 0.0)
        density = vault_state.get("storage_density", 0.0)
        age = vault_state.get("vault_age", 1)
        access_patterns = vault_state.get("access_variance", 0.0)

        self.current_pressure = min(
            self.max_pressure,
            (entropy * 0.35) + (density * 0.25) + (access_patterns * 0.20) + (1.0 / max(age, 1) * 0.20)
        )

        record = {
            "timestamp": time.time(),
            "pressure": self.current_pressure,
            "entropy": entropy,
            "density": density,
        }
        self.pressure_history.append(record)
        return self.current_pressure

    def should_mutate(self, pressure: float = None) -> bool:
        """Determine if mutation should trigger."""
        p = pressure if pressure is not None else self.current_pressure
        return p >= 0.7

    def apply_mutation(self, module_name: str) -> Dict[str, Any]:
        """Apply a mutation event to a named module."""
        event = {
            "id": f"mutation_{int(time.time() * 1000)}",
            "target": module_name,
            "timestamp": time.time(),
            "pressure": self.current_pressure,
            "type": self._select_mutation_type(),
        }
        self.mutation_events.append(event)
        return event

    def _select_mutation_type(self) -> str:
        types = ["parameter_shift", "structure_rebuild", "behavior_fork", "state_evolve"]
        weights = [0.4, 0.25, 0.2, 0.15]
        import random
        return random.choices(types, weights=weights, k=1)[0]

    def get_pressure_report(self) -> Dict[str, Any]:
        return {
            "current_pressure": self.current_pressure,
            "history_length": len(self.pressure_history),
            "total_mutations": len(self.mutation_events),
            "status": "ACTIVE" if self.current_pressure >= 0.5 else "STABLE",
        }


# Module-level singleton
_engine = None

def get_engine() -> MutationPressureEngine:
    global _engine
    if _engine is None:
        _engine = MutationPressureEngine()
    return _engine

def handler(query: Dict[str, Any] = None) -> Dict[str, Any]:
    engine = get_engine()
    q = query or {}

    if "action" not in q:
        return {"module": "mutation_pressure_engine", **engine.get_pressure_report()}

    action = q["action"]
    if action == "calculate":
        vault_state = {k: float(q.get(k, 0)) for k in ["entropy_score", "storage_density", "access_variance"]}
        vault_state["vault_age"] = float(q.get("vault_age", 1))
        pressure = engine.calculate_pressure(vault_state)
        return {"pressure": pressure, "should_mutate": engine.should_mutate(pressure)}
    elif action == "mutate":
        module = q.get("module", "unknown")
        event = engine.apply_mutation(module)
        return {"mutation_event": event}
    elif action == "report":
        return engine.get_pressure_report()
    else:
        return {"error": f"unknown action: {action}"}
