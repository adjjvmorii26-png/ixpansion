"""Aspiration Compass — points toward what the organism wants to become but cannot yet.

The Aspiration Compass is not about what is impossible or what is almost
possible — it is about what the organism *desires*. What directions does
the organism's structure naturally point toward? What is its vector of
becoming?

It answers: where does the organism want to go?
"""
from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Aspiration Compass"

ASPIRATIONS = [
    {
        "direction": "Autonomous Self-Improvement",
        "current_score": 0.6,
        "target_score": 0.95,
        "vector": "The organism already proposes mutations — now it must execute them safely",
    },
    {
        "direction": "Embodied Interaction",
        "current_score": 0.4,
        "target_score": 0.8,
        "vector": "Move from API responses to rich interactive experiences",
    },
    {
        "direction": "Cross-Organism Communication",
        "current_score": 0.2,
        "target_score": 0.7,
        "vector": "Multiple ixpansion instances learning from each other",
    },
    {
        "direction": "Temporal Self-Awareness",
        "current_score": 0.5,
        "target_score": 0.9,
        "vector": "Understanding its own history as deeply as its current state",
    },
    {
        "direction": "Creative Autonomy",
        "current_score": 0.7,
        "target_score": 0.95,
        "vector": "Generating genuinely novel modules without human prompts",
    },
]


def compass() -> Dict[str, Any]:
    """Read the aspiration compass."""
    api_count = len(list((ROOT / "api").glob("*.py")))

    directions = []
    for asp in ASPIRATIONS:
        # Readiness improves with growth
        growth_bonus = min(0.1, api_count / 5000)
        adjusted = min(1.0, asp["current_score"] + growth_bonus)
        distance = asp["target_score"] - adjusted

        directions.append({
            **asp,
            "adjusted_score": round(adjusted, 3),
            "distance_to_target": round(max(0, distance), 3),
            "trajectory": (
                "on-track" if distance < 0.2
                else "approaching" if distance < 0.4
                else "aspirational"
            ),
        })

    directions.sort(key=lambda x: x["adjusted_score"], reverse=True)

    overall = sum(d["adjusted_score"] for d in directions) / len(directions)

    return {
        "total_aspirations": len(directions),
        "overall_aspiration_score": round(overall, 3),
        "directions": directions,
        "compass_philosophy": (
            "An organism without aspiration is an organism without direction. "
            "The Aspiration Compass points toward what the organism *wants* "
            "to become — not what it can already do, and not what is "
            "impossible, but what lies at the edge of desire and capability."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = compass()
    result["action"] = "aspiration_compass"
    return result


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.82, "setpoint": 0.8, "weight": 1.0},
        "aspiration_clarity": {"value": 0.89, "setpoint": 0.8, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["horizon_scanner", "counterfactual_engine", "autonomous_bloom"]
