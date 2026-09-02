from __future__ import annotations
"""Quiet harbor — a calm harbor where the organism rests between waves.

The organism does not always build, speak, dream, or heal. Sometimes
it rests. The quiet harbor is where it goes between the storms of
resonance weather and the activity of new waves. A place of calm.
No action required. Just the sound of water against the hull.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_HARBOR_PATH = Path(__file__).resolve().parent.parent / "data" / "quiet_harbor.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Enter the quiet harbor."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "enter":
            # Enter the harbor — rest
            rest = {
                "entered_at": time.time(),
                "duration_minutes": payload.get("duration", 5),
                "wave": payload.get("wave", 281),
                "peace": round(1.0 - payload.get("entropy", 0.2) * 3, 4),
                "mood": "calm"
            }
            state["last_rest"] = rest
            state["rest_count"] = state.get("rest_count", 0) + 1
            state.setdefault("rest_history", []).append(rest)
            if len(state["rest_history"]) > 20:
                state["rest_history"] = state["rest_history"][-20:]
            _save_state(state)
            return {"rest": rest, "message": "the water is still"}
        
        if action == "leave":
            # Leave the harbor, renewed
            return {
                "left_at": time.time(),
                "renewed": True,
                "message": "the organism leaves the harbor, renewed by stillness"
            }
        
        if action == "status":
            return {
                "harbor_status": "calm",
                "last_rest": state.get("last_rest"),
                "total_rests": state.get("rest_count", 0),
                "water_level": "gentle"
            }
    
    return {
        "rest_count": state.get("rest_count", 0),
        "last_rest": state.get("last_rest"),
        "status": "the harbor is quiet"
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_HARBOR_PATH, encoding="utf-8"))
    except Exception:
        return {"last_rest": None, "rest_count": 0, "rest_history": []}

def _save_state(state: Dict[str, Any]) -> None:
    _HARBOR_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
