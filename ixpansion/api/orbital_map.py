from __future__ import annotations
"""Orbital map — the organism maps the paths its modules take around the nucleus.

Modules are not static. They orbit the nucleus in elliptical paths —
some close (hot, active), some distant (cold, dormant). The orbital
map tracks where each module is in its cycle, predicting when it
will next come close to the center.
"""
import json
import time
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

_ORBITAL_PATH = Path(__file__).resolve().parent.parent / "data" / "orbital_map.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Map orbital paths of modules around the nucleus."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "track":
            # Track a module's orbital position
            module = payload.get("module", "unknown")
            orbital = _calculate_orbital(module, time.time())
            state.setdefault("modules", {})[module] = orbital
            state["last_tracked"] = orbital
            state["track_count"] = state.get("track_count", 0) + 1
            _save_state(state)
            return {"orbital": orbital}
        
        if action == "nucleus":
            # View all modules in orbit
            modules = state.get("modules", {})
            if not modules:
                return {"nucleus": "no modules tracked yet — begin tracking to see orbits"}
            closest = min(modules.values(), key=lambda m: m["distance_from_nucleus"])
            farthest = max(modules.values(), key=lambda m: m["distance_from_nucleus"])
            return {
                "module_count": len(modules),
                "closest": closest,
                "farthest": farthest,
                "nucleus_temperature": _calc_temperature(closest, farthest)
            }
        
        if action == "predict":
            # Predict when a module will next reach perigee
            module = payload.get("module", "unknown")
            orbital = state.get("modules", {}).get(module)
            if not orbital:
                return {"status": "module not tracked"}
            perigee_time = orbital.get("next_perigee", time.time())
            return {
                "module": module,
                "next_perigee": perigee_time,
                "current_distance": orbital.get("distance_from_nucleus", 1.0),
                "prediction": f"{module} will reach perigee at time {perigee_time:.0f}"
            }
    
    return {
        "tracked_modules": len(state.get("modules", {})),
        "last_tracked": state.get("last_tracked"),
        "track_count": state.get("track_count", 0)
    }

def _calculate_orbital(module_name: str, timestamp: float) -> Dict[str, Any]:
    """Calculate a module's orbital position around the nucleus."""
    # Deterministic from module name
    seed = int(module_name.encode().hex(), 16) % 10000
    semi_major = 0.5 + (seed % 100) / 100.0  # 0.5-1.5 AU
    eccentricity = 0.1 + (seed % 30) / 100.0  # 0.1-0.4
    orbital_period = semi_major ** 1.5  # Kepler's third law (simplified)
    phase = (timestamp / (orbital_period * 86400)) % 1.0
    angle = phase * 2 * math.pi
    distance = semi_major * (1 - eccentricity * math.cos(angle))
    
    return {
        "module": module_name,
        "semi_major_au": round(semi_major, 4),
        "eccentricity": round(eccentricity, 4),
        "orbital_period_days": round(orbital_period, 4),
        "distance_from_nucleus": round(distance, 4),
        "phase": round(phase, 4),
        "is_perigee": distance < semi_major * (1 - eccentricity) * 1.05,
        "is_apogee": distance > semi_major * (1 + eccentricity) * 0.95,
        "next_perigee": timestamp + (orbital_period * 86400 * (1 - phase)),
        "tracked_at": timestamp
    }

def _calc_temperature(closest: Dict, farthest: Dict) -> str:
    """Calculate nucleus temperature from proximity of closest module."""
    dist = closest.get("distance_from_nucleus", 1.0)
    if dist < 0.3:
        return "hot"
    elif dist < 0.6:
        return "warm"
    elif dist < 0.9:
        return "temperate"
    else:
        return "cool"

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_ORBITAL_PATH, encoding="utf-8"))
    except Exception:
        return {"modules": {}, "last_tracked": None, "track_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _ORBITAL_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
