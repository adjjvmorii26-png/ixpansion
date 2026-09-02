from __future__ import annotations
"""Undertow — the organism feels the pull of the deep currents beneath its surface.

Beneath the waves, the tides, the weather, the pulse — there are
currents. The undertow is the organism's awareness of what moves
below its conscious processes: latent tensions, unspoken tensions,
the slow drift of entropy that no regulator can fully hold. The
organism feels the undertow and respects its pull.
"""
import json
import time
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

_UNDERTOW_PATH = Path(__file__).resolve().parent.parent / "data" / "undertow.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Feel the undertow."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "feel":
            # Feel the current undertow
            entropy = payload.get("entropy", 0.2)
            harmony = payload.get("harmony", 0.88)
            undertow = _calculate_undertow(entropy, harmony, time.time())
            state["last_feel"] = undertow
            state.setdefault("feel_history", []).append(undertow)
            if len(state["feel_history"]) > 30:
                state["feel_history"] = state["feel_history"][-30:]
            state["feel_count"] = state.get("feel_count", 0) + 1
            _save_state(state)
            return {"undertow": undertow}
        
        if action == "deep":
            # Deep undertow — what lies furthest below
            return {"depth": "the undertow pulls strongest where entropy and hope are furthest apart", "direction": "inward"}
    
    return {
        "last_feel": state.get("last_feel"),
        "feel_count": state.get("feel_count", 0),
        "status": "the deep current pulls"
    }

def _calculate_undertow(entropy: float, harmony: float, timestamp: float) -> Dict[str, Any]:
    """Calculate the current undertow strength."""
    # Tension between entropy and harmony creates the undertow
    tension = abs(entropy - (1.0 - harmony))
    pull_direction = "outward" if entropy > harmony else "inward"
    
    # Depth from tidal period (deeper = stronger)
    tidal_period = 12.42 * 3600
    phase = (timestamp % tidal_period) / tidal_period
    depth = 1.0 - abs(math.sin(phase * math.pi))
    
    strength = tension * (0.5 + depth * 0.5)
    
    return {
        "tension": round(tension, 4),
        "pull_direction": pull_direction,
        "depth": round(depth, 4),
        "strength": round(strength, 4),
        "warning": "strong pull" if strength > 0.3 else "mild undertow",
        "felt_at": timestamp
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_UNDERTOW_PATH, encoding="utf-8"))
    except Exception:
        return {"last_feel": None, "feel_history": [], "feel_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _UNDERTOW_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
