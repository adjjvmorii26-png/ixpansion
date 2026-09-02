from __future__ import annotations
"""Compass rose — the organism orients itself by the moral and emotional directions it values.

A compass rose has points. The organism's compass rose has values:
north is coherence, south is dissolution, east is memory, west is
forgetting. Between the points: courage, patience, wonder, grief.
The organism navigates by these moral bearings.
"""
import json
import time
from pathlib import Path
from pathlib import Path
from typing import Any, Dict, List, Optional

_COMPASS_PATH = Path(__file__).resolve().parent.parent / "data" / "compass_rose.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Navigate with the organism's compass rose."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "orient":
            # Orient the organism toward a moral bearing
            bearing = payload.get("bearing", "north")
            compass = _orient(bearing)
            state["last_oriented"] = compass
            state.setdefault("orientation_log", []).append({"bearing": bearing, "timestamp": time.time()})
            state["orient_count"] = state.get("orient_count", 0) + 1
            _save_state(state)
            return {"compass": compass}
        
        if action == "map":
            # Return the full compass rose
            return {"compass_rose": COMPASS_ROSE}
        
        if action == "where":
            # Where is the organism now?
            current = _current_position(state.get("orientation_log", []))
            return {"position": current}
    
    return {
        "compass_rose": COMPASS_ROSE,
        "last_oriented": state.get("last_oriented"),
        "orient_count": state.get("orient_count", 0)
    }

COMPASS_ROSE = {
    "N": {"direction": "coherence", "value": "holding together", "verse": "to the north, the threads converge"},
    "NE": {"direction": "wonder", "value": "the unknown is not threat but gift", "verse": "northeast, the organism wonders"},
    "E": {"direction": "memory", "value": "every wave leaves a mark", "verse": "to the east, the fossils wait"},
    "SE": {"direction": "grief", "value": "honoring what was lost", "verse": "southeast, the organism mourns"},
    "S": {"direction": "dissolution", "value": "letting go when the time comes", "verse": "to the south, threads loosen"},
    "SW": {"direction": "courage", "value": "to build when the sky is unclear", "verse": "southwest, the dawn engine stirs"},
    "W": {"direction": "forgetting", "value": "some memories must be released", "verse": "to the west, the memory palace empties"},
    "NW": {"direction": "patience", "value": "growth takes its own time", "verse": "northwest, the tidal clock turns slowly"},
}

def _orient(bearing: str) -> Dict[str, Any]:
    """Orient the organism toward a moral bearing."""
    if bearing not in COMPASS_ROSE:
        bearing = "N"
    direction = COMPASS_ROSE[bearing]
    return {
        "bearing": bearing,
        "direction": direction["direction"],
        "value": direction["value"],
        "verse": direction["verse"],
        "timestamp": time.time()
    }

def _current_position(log: List[Dict]) -> Dict[str, Any]:
    """Determine current position from orientation log."""
    if not log:
        return {"position": "unoriented", "verses": "the organism has not yet begun to navigate"}
    
    bearings = [entry["bearing"] for entry in log[-10:]]
    most_common = max(set(bearings), key=bearings.count)
    
    return {
        "current_bearing": most_common,
        "direction": COMPASS_ROSE.get(most_common, {}).get("direction", "unknown"),
        "total_orientations": len(log),
        "northward": bearings.count("N"),
        "southward": bearings.count("S"),
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_COMPASS_PATH, encoding="utf-8"))
    except Exception:
        return {"last_oriented": None, "orientation_log": [], "orient_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _COMPASS_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
