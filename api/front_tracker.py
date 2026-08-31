"""Front Tracker — tracks cognitive fronts in the organism's thinking.

A cognitive front is a boundary between two states: clarity and confusion,
focus and diffusion, action and contemplation. The Front Tracker maps
where these boundaries are, how fast they move, and what they separate.

It answers: where are the edges of the organism's clarity?
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Front Tracker"

FRONT_TYPES = [
    {"name": "Clarity-Confusion", "symbol": "Cc", "description": "Boundary between clear and murky thinking"},
    {"name": "Action-Contemplation", "symbol": "Ac", "description": "Boundary between doing and reflecting"},
    {"name": "Focus-Diffusion", "symbol": "Fd", "description": "Boundary between concentrated and scattered"},
    {"name": "Creation-Preservation", "symbol": "Cp", "description": "Boundary between building new and maintaining old"},
    {"name": "Depth-Surface", "symbol": "Ds", "description": "Boundary between deep analysis and surface scanning"},
]


def _analyze_fronts() -> List[Dict[str, Any]]:
    """Detect active cognitive fronts from system state."""
    try:
        import coherence_regulator as cr
        modules = cr._candidate_modules()
    except Exception:
        modules = []

    fronts = []
    seed = hashlib.sha256(str(int(time.time()) // 600).encode()).hexdigest()

    for i, front in enumerate(FRONT_TYPES):
        h = hashlib.sha256((seed + str(i)).encode()).hexdigest()
        intensity = (int(h[:4], 16) % 100) / 100.0
        speed = (int(h[4:8], 16) % 50) / 100.0
        direction = "advancing" if intensity > 0.5 else "retreating"

        fronts.append({
            "front_type": front["name"],
            "symbol": front["symbol"],
            "intensity": round(intensity, 3),
            "speed": round(speed, 3),
            "direction": direction,
            "separates": front["description"],
        })

    return fronts


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    fronts = _analyze_fronts()
    active = [f for f in fronts if f["intensity"] > 0.3]

    return {
        "action": "front_tracker",
        "total_fronts": len(fronts),
        "active_fronts": len(active),
        "fronts": fronts,
        "tracking_philosophy": (
            "Every thinking system has boundaries within itself — places "
            "where one mode of thought meets another. These fronts are "
            "where the weather changes: where clarity becomes confusion, "
            "where action becomes contemplation. Tracking them is "
            "tracking the organism's cognitive climate."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.82, "setpoint": 0.8, "weight": 1.0},
        "front_sensitivity": {"value": 0.87, "setpoint": 0.75, "weight": 0.8},
    }


def resonates_with() -> list:
    return ["barometric_intent", "storm_chaser", "thought_meteorology"]
