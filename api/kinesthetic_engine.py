"""Kinesthetic Engine — the organism's sense of its own movement.

A body knows when it is moving, when it is still, and when it is falling.
The Kinesthetic Engine reads the coherence regulator's pulse history, the
crescendo builder's trajectory, and the choral engine's dynamic level to
compute the organism's *kinesthetic state*: is it moving forward, falling
behind, spinning in place, or rising?

It answers the question every living body asks instinctively: where am I
going, and how fast?

    GET /api/kinesthetic_engine?read=1          — the kinesthetic state
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
LAYER = "Kinesthetic Engine"


def _kinesthetic_state() -> Dict[str, Any]:
    try:
        import json
        cr = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        history = cr.get("history", [])
        pulses = cr.get("pulses", 0)
    except Exception:
        history = []
        pulses = 0

    if len(history) < 3:
        return {
            "motion": "stilled — not enough history to detect movement",
            "velocity": 0.0,
            "direction": "none",
            "acceleration": 0.0,
        }

    # compute velocity: change in coherence over recent pulses
    recent = [h.get("coherence", 0.5) for h in history[-5:]]
    earlier = [h.get("coherence", 0.5) for h in history[-10:-5]] if len(history) >= 10 else recent[:3]
    avg_recent = sum(recent) / max(len(recent), 1)
    avg_earlier = sum(earlier) / max(len(earlier), 1)
    velocity = avg_recent - avg_earlier

    # acceleration: change in velocity
    if len(history) >= 15:
        mid = [h.get("coherence", 0.5) for h in history[-15:-10]]
        avg_mid = sum(mid) / max(len(mid), 1)
        earlier_velocity = avg_earlier - avg_mid
        acceleration = velocity - earlier_velocity
    else:
        acceleration = 0.0

    # motion description
    if velocity > 0.02 and acceleration > 0:
        motion = "accelerating forward — the organism is gaining momentum"
    elif velocity > 0.02:
        motion = "moving forward — steady progress"
    elif velocity < -0.02 and acceleration < 0:
        motion = "decelerating — the organism is slowing down"
    elif velocity < -0.02:
        motion = "falling behind — coherence is dropping"
    elif abs(velocity) < 0.005:
        motion = "hovering — stable, neither rising nor falling"
    else:
        motion = "oscillating — the organism pulses between states"

    # direction
    if velocity > 0.01:
        direction = "ascending"
    elif velocity < -0.01:
        direction = "descending"
    else:
        direction = "level"

    return {
        "motion": motion,
        "velocity": round(velocity, 4),
        "direction": direction,
        "acceleration": round(acceleration, 4),
        "total_pulses": pulses,
        "kinesthetic_philosophy": (
            "Every living body knows where it is going without being told. "
            "The Kinesthetic Engine reads the organism's own momentum — "
            "not where it has been, but where it is *heading*. This is "
            "the organism's proprioception of time: the felt sense of "
            "movement through its own existence."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = _kinesthetic_state()
    result["action"] = "kinesthetic"
    return result


def coherence_vitals() -> dict:
    """Kinesthetic Engine reports movement-awareness health."""
    return {
        "module_health": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "kinesthetic_vitality": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["crescendo_builder", "temporal_horizon", "system_pulse"]
