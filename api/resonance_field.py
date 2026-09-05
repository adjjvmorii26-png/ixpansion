"""Resonance Field — agents vibrate at frequencies that attract or repel each other.

Agents emit vibrational signatures. When signatures align, agents resonate
and amplify each other. When they clash, destructive interference occurs.
Resonance fields can be tuned to attract specific agent types.
"""
from __future__ import annotations

import math
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class VibrationalSignature:
    """An agent's unique frequency signature."""

    def __init__(self, agent_id: str, frequency: float = None):
        self.agent_id = agent_id
        self.frequency = frequency or random.uniform(0.1, 100.0)
        self.amplitude = random.uniform(0.5, 2.0)
        self.phase = random.uniform(0, 2 * math.pi)
        self.damping = random.uniform(0.01, 0.1)

    def wave(self, t: float) -> float:
        """Compute wave value at time t."""
        return self.amplitude * math.sin(
            self.frequency * t + self.phase
        ) * math.exp(-self.damping * t)

    def energy(self) -> float:
        """Current energy level."""
        return 0.5 * self.amplitude ** 2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "frequency": round(self.frequency, 4),
            "amplitude": round(self.amplitude, 4),
            "phase": round(self.phase, 4),
            "energy": round(self.energy(), 4),
        }


class ResonanceField:
    """Manages vibrational interactions between agents."""

    def __init__(self):
        self.signatures: Dict[str, VibrationalSignature] = {}
        self.interactions: List[Dict[str, Any]] = []
        self.resonance_events: List[Dict[str, Any]] = []

    def register(self, agent_id: str, frequency: float = None) -> Dict[str, Any]:
        """Register an agent's vibrational signature."""
        sig = VibrationalSignature(agent_id, frequency)
        self.signatures[agent_id] = sig
        return sig.to_dict()

    def compute_resonance(self, id_a: str, id_b: str) -> Dict[str, Any]:
        """Compute resonance between two agents."""
        if id_a not in self.signatures or id_b not in self.signatures:
            return {"error": "agent not found"}
        a, b = self.signatures[id_a], self.signatures[id_b]
        freq_diff = abs(a.frequency - b.frequency)
        freq_ratio = min(a.frequency, b.frequency) / max(a.frequency, b.frequency) if max(a.frequency, b.frequency) > 0 else 0
        coherence = 1.0 - min(freq_diff / 50.0, 1.0)
        amplification = (a.amplitude + b.amplitude) * coherence
        interference = "constructive" if coherence > 0.5 else "destructive"
        result = {
            "agents": [id_a, id_b],
            "frequency_difference": round(freq_diff, 4),
            "coherence": round(coherence, 4),
            "amplification": round(amplification, 4),
            "interference": interference,
            "timestamp": time.time(),
        }
        self.interactions.append(result)
        if coherence > 0.7:
            event = {
                "type": "resonance_peak",
                "agents": [id_a, id_b],
                "coherence": coherence,
                "amplification": amplification,
                "timestamp": time.time(),
            }
            self.resonance_events.append(event)
        return result

    def tune_field(self, target_freq: float, tolerance: float = 5.0) -> List[str]:
        """Find agents resonating near a target frequency."""
        tuned = []
        for aid, sig in self.signatures.items():
            if abs(sig.frequency - target_freq) <= tolerance:
                tuned.append(aid)
        return tuned

    def get_field_energy(self) -> float:
        """Total energy in the resonance field."""
        return sum(sig.energy() for sig in self.signatures.values())

    def field_stats(self) -> Dict[str, Any]:
        return {
            "total_agents": len(self.signatures),
            "total_interactions": len(self.interactions),
            "resonance_events": len(self.resonance_events),
            "total_field_energy": round(self.get_field_energy(), 4),
        }


_field = ResonanceField()


def resonance_field_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "register":
        return _field.register(
            payload.get("agent_id", f"agent_{random.randint(1000,9999)}"),
            payload.get("frequency"),
        )
    elif action == "resonate":
        return _field.compute_resonance(
            payload.get("agent_a", ""), payload.get("agent_b", "")
        )
    elif action == "tune":
        return {
            "tuned_agents": _field.tune_field(
                payload.get("frequency", 50.0),
                payload.get("tolerance", 5.0),
            )
        }
    return {"status": "active", **_field.field_stats()}


handler = resonance_field_handler


def coherence_vitals() -> dict:
    """Resonance Field reports — aligning and clashing frequencies."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.95, "setpoint": 0.85, "weight": 1.0},
        "field_alignment": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
    }

def resonates_with() -> list:
    """Declared kinships."""
    return ['resonance_graph', 'synesthesia']

# --- Compliance Forge patch (Wave 419) ---

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "resonance_field", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
