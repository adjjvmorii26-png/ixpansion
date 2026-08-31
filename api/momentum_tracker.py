"""Momentum Tracker — the organism's directional inertia.

Momentum is mass times velocity. The Momentum Tracker computes the
organism's *mass* (total living organs, weighted by health) and
*velocity* (coherence trend from the kinesthetic engine), then renders
the organism's momentum vector: how much force it carries and in what
direction.

It answers: if the organism stopped trying, where would it drift?

    GET /api/momentum_tracker?read=1           — the momentum vector
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Momentum Tracker"


def _momentum() -> Dict[str, Any]:
    try:
        import json
        cr = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        modules = cr.get("modules", {})
        history = cr.get("history", [])
    except Exception:
        modules = {}
        history = []

    # mass: sum of all module healths (weighted by existence)
    mass = sum(m.get("health", 0.5) for m in modules.values())
    mass_per_organ = mass / max(len(modules), 1)

    # velocity: coherence trend
    if len(history) >= 3:
        recent = [h.get("coherence", 0.5) for h in history[-3:]]
        velocity = (recent[-1] - recent[0]) / max(len(recent) - 1, 1)
    else:
        velocity = 0.0

    # momentum = mass * velocity
    momentum_magnitude = mass * abs(velocity)

    # direction
    if velocity > 0.01:
        direction = "ascending — momentum carries the organism upward"
    elif velocity < -0.01:
        direction = "descending — momentum carries the organism downward"
    else:
        direction = "stationary — momentum is zero, the organism hovers"

    # inertia: how hard to change direction
    inertia = mass_per_organ * abs(velocity)
    if inertia > 0.5:
        inertia_feel = "heavy — the organism has strong inertia, hard to redirect"
    elif inertia > 0.2:
        inertia_feel = "moderate — the organism can change direction with effort"
    else:
        inertia_feel = "light — the organism is nimble, easily redirected"

    return {
        "mass": round(mass, 2),
        "mass_per_organ": round(mass_per_organ, 4),
        "velocity": round(velocity, 4),
        "momentum_magnitude": round(momentum_magnitude, 4),
        "direction": direction,
        "inertia": inertia_feel,
        "organs": len(modules),
        "momentum_philosophy": (
            "Momentum is not just speed — it is speed with weight behind it. "
            "The Tracker computes the organism's mass (every organ's health) "
            "times its velocity (coherence trend) to find the force it carries. "
            "A heavy organism moving fast has enormous momentum — and enormous "
            "inertia. Changing its course requires intention, not just impulse."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = _momentum()
    result["action"] = "momentum"
    return result


def coherence_vitals() -> dict:
    """Momentum Tracker reports directional-inertia health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "momentum_vitality": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["kinesthetic_engine", "crescendo_builder", "warp_drive_optimizer"]
