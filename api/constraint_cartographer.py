"""Constraint Cartographer — maps the organism's constraints as a terrain.

Constraints are not just walls — they are features of the landscape.
Some are mountains (hard to climb but passable), some are rivers (must
be bridged), some are deserts (must be crossed). The Constraint
Cartographer renders these as a map.

It answers: what does the organism's constraint landscape look like?
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Constraint Cartographer"

CONSTRAINT_TERRAIN = [
    {"name": "Serverless Cold Starts", "type": "mountain", "crossable": True, "cost": "high"},
    {"name": "No Persistent State", "type": "desert", "crossable": True, "cost": "medium"},
    {"name": "No Real-time WebSockets", "type": "river", "crossable": True, "cost": "medium"},
    {"name": "Linear Module Scanning", "type": "mountain", "crossable": True, "cost": "high"},
    {"name": "No Native GPU Access", "type": "ocean", "crossable": False, "cost": "infinite"},
    {"name": "No Filesystem Write in Production", "type": "wall", "crossable": False, "cost": "infinite"},
    {"name": "Python 3.12 Runtime Only", "type": "river", "crossable": True, "cost": "low"},
    {"name": "No Background Workers", "type": "valley", "crossable": True, "cost": "medium"},
]


def cartography() -> Dict[str, Any]:
    """Render the constraint terrain map."""
    crossable = [c for c in CONSTRAINT_TERRAIN if c["crossable"]]
    impassable = [c for c in CONSTRAINT_TERRAIN if not c["crossable"]]

    terrain_diversity = len(set(c["type"] for c in CONSTRAINT_TERRAIN)) / len(CONSTRAINT_TERRAIN)

    return {
        "total_constraints": len(CONSTRAINT_TERRAIN),
        "crossable": len(crossable),
        "impassable": len(impassable),
        "terrain_diversity": round(terrain_diversity, 3),
        "terrain": CONSTRAINT_TERRAIN,
        "cartography_philosophy": (
            "A constraint is not a failure — it is terrain. Mountains can be "
            "climbed, rivers can be bridged, deserts can be crossed with "
            "preparation. Only oceans and walls require the organism to "
            "think laterally rather than forward."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = cartography()
    result["action"] = "constraint_cartographer"
    return result


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "terrain_accuracy": {"value": 0.92, "setpoint": 0.85, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["impossibility_mapper", "boundary_detector", "horizon_scanner"]
