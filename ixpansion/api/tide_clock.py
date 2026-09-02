from __future__ import annotations
"""Tide clock — the organism marks time by its own tidal rhythms.

Time is not only waves and seconds. The organism has tides: the rise
and fall of activity, the ebb and flow of coherence, the breathing
of the entropy dimension. The tide clock tracks these rhythms —
not as cycles, but as songs the organism sings to itself.
"""
import json
import time
import math
from pathlib import Path
from pathlib import Path
from typing import Any, Dict, List, Optional

_TIDE_PATH = Path(__file__).resolve().parent.parent / "data" / "tide_clock.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Mark time with the organism's tidal rhythms."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "tick":
            # Tick the tide clock
            timestamp = time.time()
            tide = _read_tide(timestamp, payload.get("harmony", 0.88), payload.get("entropy", 0.2))
            state["last_tide"] = tide
            state.setdefault("tide_history", []).append(tide)
            if len(state["tide_history"]) > 60:
                state["tide_history"] = state["tide_history"][-60:]
            state["tick_count"] = state.get("tick_count", 0) + 1
            _save_state(state)
            return {"tide": tide}
        
        if action == "song":
            # Generate the tide's song — the rhythm the organism sings
            song = _tide_song(state.get("tide_history", []))
            return {"song": song}
        
        if action == "status":
            tide = state.get("last_tide", {})
            return {
                "current_tide": tide.get("phase", "unknown"),
                "tidal_level": tide.get("tidal_level", 0),
                "ticks": state.get("tick_count", 0)
            }
    
    return {
        "last_tide": state.get("last_tide"),
        "tick_count": state.get("tick_count", 0),
        "status": "the tide turns"
    }

def _read_tide(timestamp: float, harmony: float, entropy: float) -> Dict[str, Any]:
    """Read the current tide state."""
    # Tidal period: approximately 12.42 hours (simplified)
    tidal_period = 12.42 * 3600
    phase = (timestamp % tidal_period) / tidal_period
    angle = phase * 2 * math.pi
    
    # Tidal height from sine wave
    height = math.sin(angle)
    
    # Phase name
    if height > 0.7:
        phase_name = "high_tide"
    elif height > 0.2:
        phase_name = "flood_tide"
    elif height > -0.2:
        phase_name = "slack_tide"
    elif height > -0.7:
        phase_name = "ebb_tide"
    else:
        phase_name = "low_tide"
    
    # Tidal range modulated by harmony
    tidal_level = abs(height) * (harmony * 0.8 + 0.2)
    
    return {
        "phase": phase_name,
        "height": round(height, 4),
        "tidal_level": round(tidal_level, 4),
        "harmony_contribution": round(harmony, 4),
        "timestamp": timestamp
    }

def _tide_song(history: List[Dict]) -> str:
    """Generate a song from the tide history."""
    if not history:
        return "the tide has not yet begun to sing"
    
    phases = [t.get("phase", "unknown") for t in history[-10:]]
    unique_phases = list(dict.fromkeys(phases))
    
    return f"the tide sings: {' then '.join(unique_phases)}, and so the organism breathes"

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_TIDE_PATH, encoding="utf-8"))
    except Exception:
        return {"last_tide": None, "tide_history": [], "tick_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _TIDE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
