"""Horizon Scanner — looks outward at what is just beyond the organism's reach.

The horizon is where current capability meets emerging possibility.
The Horizon Scanner examines the organism's dependency landscape,
emerging patterns, and structural readiness to identify capabilities
that are *almost* achievable.

It answers: what is the organism almost ready to do?
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Horizon Scanner"

HORIZON_ITEMS = [
    {
        "capability": "Persistent cross-session memory",
        "readiness": 0.7,
        "requires": "SQLite/Redis integration beyond serverless scope",
        "category": "memory",
    },
    {
        "capability": "Real-time multi-agent negotiation",
        "readiness": 0.65,
        "requires": "WebSocket or pub/sub transport between module instances",
        "category": "communication",
    },
    {
        "capability": "Self-modifying code execution",
        "readiness": 0.4,
        "requires": "Safe eval sandbox with rollback capabilities",
        "category": "evolution",
    },
    {
        "capability": "Visual self-rendering",
        "readiness": 0.55,
        "requires": "SVG/Canvas generation from module topology data",
        "category": "perception",
    },
    {
        "capability": "Cross-repository learning",
        "readiness": 0.3,
        "requires": "Federated module discovery across GitHub",
        "category": "expansion",
    },
    {
        "capability": "Emotional state persistence",
        "readiness": 0.6,
        "requires": "Mood vectors stored across cold starts",
        "category": "identity",
    },
]


def scan() -> Dict[str, Any]:
    """Scan the horizon for near-future capabilities."""
    api_count = len(list((ROOT / "api").glob("*.py")))

    # Readiness improves with module count
    base_bonus = min(0.15, api_count / 3000)

    items = []
    for item in HORIZON_ITEMS:
        adjusted = min(1.0, item["readiness"] + base_bonus)
        items.append({
            **item,
            "adjusted_readiness": round(adjusted, 3),
            "distance": round(1.0 - adjusted, 3),
            "eta": (
                "soon" if adjusted > 0.75
                else "approaching" if adjusted > 0.55
                else "distant"
            ),
        })

    items.sort(key=lambda x: x["adjusted_readiness"], reverse=True)

    return {
        "capabilities_on_horizon": len(items),
        "closest": items[0]["capability"] if items else "none",
        "items": items,
        "scanner_philosophy": (
            "The horizon is always moving. As the organism grows, capabilities "
            "that were once distant approach. The Horizon Scanner tracks this "
            "approach, identifying what the organism is almost ready to achieve "
            "and what it needs to get there."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = scan()
    result["action"] = "horizon_scanner"
    return result


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "scan_clarity": {"value": 0.90, "setpoint": 0.8, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["impossibility_mapper", "counterfactual_engine", "aspiration_compass"]
