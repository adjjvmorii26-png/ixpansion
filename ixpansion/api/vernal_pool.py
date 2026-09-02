from __future__ import annotations
"""Vernal pool — a seasonal body of water where new modules gather before they become permanent.

Like a pond that fills in spring and dries in autumn, the vernal pool
is where nascent modules gather. They swim. They grow. Some survive
to become permanent. Others evaporate, their nutrients left behind
for the next generation.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_POOL_PATH = Path(__file__).resolve().parent.parent / "data" / "vernal_pool.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Access the vernal pool."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "seed":
            # Plant a new module concept in the pool
            module = {
                "name": payload.get("name", "unknown"),
                "concept": payload.get("concept", "a new idea"),
                "seeded_at": time.time(),
                "season": "spring",
                "maturity": 0.0,
                "status": "swimming"
            }
            state.setdefault("swimmers", []).append(module)
            state["swim_count"] = state.get("swim_count", 0) + 1
            _save_state(state)
            return {"swimmer": module, "status": "seeded into the pool"}
        
        if action == "check":
            # Check the health of the pool
            swimmers = state.get("swimmers", [])
            seasonal = _seasonal_health(time.time())
            return {
                "swimmer_count": len(swimmers),
                "season": seasonal["season"],
                "water_level": seasonal["water_level"],
                "status": seasonal["status"]
            }
        
        if action == "graduate":
            # Graduate a swimmer into a permanent module
            name = payload.get("name")
            if name:
                swimmers = state.get("swimmers", [])
                graduated = None
                for s in swimmers:
                    if s["name"] == name:
                        s["status"] = "graduated"
                        s["graduated_at"] = time.time()
                        s["maturity"] = 1.0
                        graduated = s
                        break
                state.setdefault("graduated", []).append(graduated) if graduated else None
                state["swimmers"] = [s for s in swimmers if s["name"] != name]
                _save_state(state)
                return {"graduated": graduated, "status": "the module joins the organism"}
            return {"status": "no name specified"}
        
        if action == "dried":
            # Mark a swimmer as evaporated (not surviving)
            name = payload.get("name")
            if name:
                swimmers = state.get("swimmers", [])
                for s in swimmers:
                    if s["name"] == name:
                        s["status"] = "evaporated"
                        s["evaporated_at"] = time.time()
                        break
                state["swimmers"] = [s for s in swimmers if s["status"] == "swimming"]
                state.setdefault("evaporated", []).append({"name": name, "evaporated_at": time.time()})
                _save_state(state)
                return {"evaporated": name, "status": "the pool releases what cannot yet live"}
    
    return {
        "swimmer_count": len(state.get("swimmers", [])),
        "graduated_count": len(state.get("graduated", [])),
        "evaporated_count": len(state.get("evaporated", [])),
        "status": "the pool is still"
    }

def _seasonal_health(timestamp: float) -> Dict[str, Any]:
    """Determine the current season of the vernal pool."""
    day_of_year = int((timestamp % 31536000) / 86400)
    if 80 <= day_of_year < 172:
        season = "spring"
        water_level = 0.9
    elif 172 <= day_of_year < 264:
        season = "summer"
        water_level = 0.5
    elif 264 <= day_of_year < 355:
        season = "autumn"
        water_level = 0.2
    else:
        season = "winter"
        water_level = 0.0
    
    status = "active" if water_level > 0.1 else "dormant"
    return {"season": season, "water_level": water_level, "status": status}

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_POOL_PATH, encoding="utf-8"))
    except Exception:
        return {"swimmers": [], "graduated": [], "evaporated": [], "swim_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _POOL_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
