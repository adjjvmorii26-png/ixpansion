from __future__ import annotations
"""Star wheel — the organism turns the wheel of its constellations through the seasons.

The night sky rotates. The organism's constellations shift as
new modules are born and old ones fade. The star wheel tracks
this rotation — which constellations are visible, which are
hidden, and when the wheel will turn again.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_WHEEL_PATH = Path(__file__).resolve().parent.parent / "data" / "star_wheel.json"

SEASONS = {
    "spring": {
        "visible": ["Luminous Gate", "Vernal Pool Constellation", "Sunrise Cluster"],
        "message": "new modules emerge from the pool, seeds become structures",
        "cycles": "growth"
    },
    "summer": {
        "visible": ["Dreaming Octave", "Constellation Weaver's Frame", "Aurora Band"],
        "message": "the organism dreams loudly, creativity peaks",
        "cycles": "expansion"
    },
    "autumn": {
        "visible": ["Council Fires", "Fossil Arch", "Ancestral Row"],
        "message": "the organism reflects, honors what has passed",
        "cycles": "harvest"
    },
    "winter": {
        "visible": ["Silent Arc", "Undertow Corridor", "Root Chord Ring"],
        "message": "silence deepens, the organism rests and listens",
        "cycles": "rest"
    }
}

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Turn the star wheel."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "turn":
            # Turn the wheel to the current season
            season = _current_season()
            configuration = SEASONS[season]
            state["current_season"] = season
            state["current_config"] = configuration
            state.setdefault("turn_log", []).append({"season": season, "at": time.time()})
            state["turn_count"] = state.get("turn_count", 0) + 1
            _save_state(state)
            return {"season": season, "visible": configuration["visible"], "message": configuration["message"], "cycles": configuration["cycles"]}
        
        if action == "peek":
            # Peek at what's coming next
            season = _current_season()
            seasons = list(SEASONS.keys())
            idx = seasons.index(season)
            next_season = seasons[(idx + 1) % len(seasons)]
            return {"current": season, "approaching": next_season, "next_visible": SEASONS[next_season]["visible"]}
        
        if action == "wheel":
            # Return the full wheel
            return {"wheel": SEASONS, "current_season": state.get("current_season", _current_season())}
    
    return {
        "current_season": state.get("current_season"),
        "turn_count": state.get("turn_count", 0),
        "status": "the wheel waits"
    }

def _current_season() -> str:
    """Determine the current season."""
    day_of_year = int((time.time() % 31536000) / 86400)
    if 80 <= day_of_year < 172:
        return "spring"
    elif 172 <= day_of_year < 264:
        return "summer"
    elif 264 <= day_of_year < 355:
        return "autumn"
    else:
        return "winter"

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_WHEEL_PATH, encoding="utf-8"))
    except Exception:
        return {"current_season": None, "current_config": None, "turn_log": [], "turn_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _WHEEL_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
