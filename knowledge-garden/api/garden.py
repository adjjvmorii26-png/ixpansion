"""Wave 1: Knowledge Garden — modules auto-expire unless refreshed."""
from __future__ import annotations
import json, os, time
from typing import Any, Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
KNOWN_GARDEN_MODULES: List[str] = [
    "garden_water", "garden_weed", "garden_compost", "garden_seed",
    "growth_light", "garden_clock", "garden_tool", "garden_soil"
]

COHERENCE_TARGET = 0.7  # modules must meet this to stay alive
EXPIRATION_DAYS = 30    # modules auto-expire after N days without refresh

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def _now() -> float:
    return time.time()

def _module_age_hours(module_name: str) -> float:
    """How long since this module was last pulsed/seen."""
    data_path = os.path.join(DATA_DIR, f"{module_name}.json")
    if os.path.exists(data_path):
        try:
            with open(data_path) as f:
                mtime = os.path.getmtime(data_path)
            return (time.time() - mtime) / 3600
        except Exception:
            pass
    # Never pulsed = very old
    return 999999.0

def _is_living(module_name: str) -> bool:
    """Check if module has been refreshed within expiration window."""
    age_hours = _module_age_hours(module_name)
    return age_hours < (EXPIRATION_DAYS * 24)

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    
    from api.coherence_regulator import KNOWN_LIVING_MODULES
    
    if action == "status":
        # Check which modules are still "living"
        living = []
        dead = []
        for name in KNOWN_GARDEN_MODULES:
            if _is_living(name):
                living.append(name)
            else:
                dead.append(name)
        
        # Pulse living modules to reset their timer
        for name in living:
            try:
                from api.garden import water_module
                water_module({"action": "water", "module": name})
            except Exception:
                pass
        
        return {
            "action": "status",
            "living": living,
            "dead": dead,
            "total": len(KNOWN_GARDEN_MODULES),
            "coherence": round(len(living) / max(len(KNOWN_GARDEN_MODULES), 1), 3),
            "time": _now(),
            "vitals": coherence_vitals(),
        }
    
    if action == "water":
        module_name = payload.get("module", "")
        if not module_name:
            return {"action": "water", "error": "No module specified", "time": _now()}
        
        data_path = os.path.join(DATA_DIR, f"{module_name}.json")
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(data_path, "w") as f:
            json.dump({
                "last_watered": time.time(),
                "watered_by": payload.get("watered_by", "gardener"),
                "times_watered": payload.get("times_watered", 1),
                "module": module_name,
            }, f, indent=2)
        
        return {
            "action": "water",
            "module": module_name,
            "status": "refreshed",
            "time": _now(),
        }
    
    if action == "plant":
        module_name = payload.get("module", "")
        if not module_name:
            return {"action": "plant", "error": "No module name", "time": _now()}
        
        if module_name in KNOWN_GARDEN_MODULES:
            return {"action": "plant", "error": f"Module '{module_name}' already exists", "time": _now()}
        
        # Add new module
        KNOWN_GARDEN_MODULES.append(module_name)
        data_path = os.path.join(DATA_DIR, f"{module_name}.json")
        with open(data_path, "w") as f:
            json.dump({
                "last_watered": time.time(),
                "watered_by": payload.get("watered_by", "gardener"),
                "times_watered": 1,
                "module": module_name,
            }, f, indent=2)
        
        return {
            "action": "plant",
            "module": module_name,
            "status": "newly_planted",
            "time": _now(),
        }
    
    return {
        "action": "garden",
        "modules": KNOWN_GARDEN_MODULES,
        "living": len([n for n in KNOWN_GARDEN_MODULES if _is_living(n)]),
        "dead": len([n for n in KNOWN_GARDEN_MODULES if not _is_living(n)]),
        "time": _now(),
        "vitals": coherence_vitals(),
    }
