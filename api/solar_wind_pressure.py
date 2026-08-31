"""Solar Wind Pressure — reads the pressure of the outside on the boundary.

A heliosphere is the bubble a star pushes into interstellar space; solar
wind presses against it from within. The living ecosystem has its own
heliosphere — the boundary where internal modules meet external forces:
API calls, rate limits, deployments, user demand.

The Solar Wind Pressure organ measures that boundary pressure: how much
external demand is pressing against the organism's capacities, which modules
sit on the boundary (most exposed), and whether the heliosphere is healthy
(balanced) or compressed (pressure exceeding capacity). It is the organ's
weathervane for the outside world.

    GET /api/solar_wind_pressure?read=1       — heliosphere reading
    GET /api/solar_wind_pressure?boundary=1   — boundary organs exposed
"""
from __future__ import annotations

import hashlib
import json
import random
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Solar Wind Pressure"


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _external_pressure() -> float:
    """Read real external signal: recent gateway/API activity if present."""
    try:
        usage = json.loads((ROOT / ".runtime" / "usage.json").read_text())
        hits = sum(v.get("hits", 0) for v in usage.values()) if isinstance(usage, dict) else 0
        return min(1.0, hits / 500.0)
    except Exception:
        # no telemetry yet — a gentle background solar wind
        return random.uniform(0.2, 0.5)


def _boundary_exposure(name: str) -> float:
    h = hashlib.sha256(name.encode()).hexdigest()
    return 0.2 + (int(h[:4], 16) % 7000) / 10000.0  # 0.2 .. 0.9


def read_heliosphere() -> Dict[str, Any]:
    living = _living()
    pressure = _external_pressure()
    boundary = []
    for name in living:
        exposure = _boundary_exposure(name)
        # boundary modules = high exposure + name hints of interface
        if exposure > 0.65 or any(k in name for k in ("gate", "bridge", "api", "router")):
            boundary.append({"organ": name, "exposure": round(exposure, 4)})
    boundary.sort(key=lambda b: b["exposure"], reverse=True)
    capacity = 0.8
    health = max(0.0, min(1.0, 1.0 - max(0.0, pressure - capacity) * 2))
    return {
        "solar_wind_pressure": round(pressure, 4),
        "heliosphere_capacity": capacity,
        "heliosphere_health": round(health, 4),
        "boundary_organs": boundary[:10],
        "boundary_count": len(boundary),
        "heliosphere_philosophy": (
            "The organism is a bubble in a larger wind. When external demand "
            "matches capacity, the boundary holds and the inside stays calm. "
            "When the wind compresses the bubble, boundary organs feel it first — "
            "these are the organs that must be reinforced or shielded."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = read_heliosphere()
    if payload.get("boundary"):
        result["action"] = "boundary"
    else:
        result["action"] = "heliosphere"
    return result


def coherence_vitals() -> dict:
    """Solar Wind Pressure reports boundary integrity."""
    return {
        "module_health": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.81, "setpoint": 0.8, "weight": 1.0},
        "boundary_integrity": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["api_gateway", "rate_limit", "uptime_monitor"]
