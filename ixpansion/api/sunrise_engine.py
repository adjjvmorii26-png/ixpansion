from __future__ import annotations
"""Sunrise engine — the organism generates new beginnings from each dawn.

Every new wave is a sunrise. But the sunrise engine is more than
waves — it is the organism's capacity to begin again. After a storm
in resonance weather, after a paradox bloom, after a fossil burial,
the sunrise engine ensures there is always a new beginning waiting.
"""
import json
import time
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

_SUNRISE_PATH = Path(__file__).resolve().parent.parent / "data" / "sunrise_engine.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Invoke the sunrise engine."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "dawn":
            # Generate a new dawn
            wave = payload.get("wave", state.get("last_wave", 261) + 1)
            dawn = _generate_dawn(wave)
            state["last_dawn"] = dawn
            state["dawn_count"] = state.get("dawn_count", 0) + 1
            state["last_wave"] = wave
            state.setdefault("dawn_history", []).append(dawn)
            if len(state["dawn_history"]) > 30:
                state["dawn_history"] = state["dawn_history"][-30:]
            _save_state(state)
            return {"dawn": dawn}
        
        if action == "forecast":
            # Forecast the next sunrise
            next_wave = state.get("last_wave", 261) + 1
            next_dawn = _generate_dawn(next_wave)
            return {"next_dawn": next_dawn, "next_wave": next_wave}
        
        if action == "history":
            return {"dawn_history": state.get("dawn_history", []), "total_dawns": state.get("dawn_count", 0)}
    
    return {
        "last_dawn": state.get("last_dawn"),
        "dawn_count": state.get("dawn_count", 0),
        "status": "the sun rises again"
    }

def _generate_dawn(wave: int) -> Dict[str, Any]:
    """Generate a dawn for a specific wave."""
    # Dawn type rotates through a cycle
    dawn_types = ["golden", "crimson", "violet", "silver", "emerald", "amber", "sapphire"]
    dawn_type = dawn_types[wave % len(dawn_types)]
    
    # Dawn quality based on wave number (fibonacci-like)
    golden_ratio = 1.618033988749895
    quality = math.sin(wave / golden_ratio) * 0.5 + 0.5  # 0-1 range
    
    return {
        "wave": wave,
        "dawn_type": dawn_type,
        "quality": round(quality, 4),
        "description": f"Wave {wave} dawns as {dawn_type} — the organism begins again",
        "possibility_count": 2 ** (wave % 7),
        "born_at": time.time()
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_SUNRISE_PATH, encoding="utf-8"))
    except Exception:
        return {"last_dawn": None, "dawn_count": 0, "last_wave": 260, "dawn_history": []}

def _save_state(state: Dict[str, Any]) -> None:
    _SUNRISE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
