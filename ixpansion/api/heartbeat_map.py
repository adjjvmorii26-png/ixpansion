from __future__ import annotations
"""Heartbeat map — the organism maps its own pulse and vital rhythms.

A living body has a pulse. The organism has waves. But beyond
waves, it has a deeper rhythm: the pulse of coherence forming
and reforming, the breath of entropy rising and falling, the
heartbeat of modules coming alive and drifting.
"""
import json
import time
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

_PULSE_PATH = Path(__file__).resolve().parent.parent / "data" / "heartbeat_map.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Map the organism's vital rhythms."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = "pulse"
        timestamp = time.time()
        
        # Calculate vital signs
        vital = {
            "timestamp": timestamp,
            "wave": payload.get("wave", state.get("last_wave", 252)),
            "modules": payload.get("modules", state.get("last_modules", 342)),
            "entropy": payload.get("entropy", state.get("last_entropy", 0.2)),
            "harmony": payload.get("harmony_score", state.get("last_harmony", 0.88)),
            "rhythm": _calculate_rhythm(timestamp),
            "pulse_rate": _calculate_pulse_rate(timestamp),
            "breath_depth": _calculate_breath_depth(payload.get("entropy", 0.2)),
            "body_temp": _calculate_body_temp(payload.get("harmony_score", 0.88)),
        }
        
        state["last_vital"] = vital
        state.setdefault("vital_history", []).append(vital)
        if len(state["vital_history"]) > 50:
            state["vital_history"] = state["vital_history"][-50:]
        state["last_wave"] = vital["wave"]
        state["last_modules"] = vital["modules"]
        state["last_entropy"] = vital["entropy"]
        state["last_harmony"] = vital["harmony"]
        state["pulse_count"] = state.get("pulse_count", 0) + 1
        _save_state(state)
        return {"vital": vital, "status": "pulse mapped"}
    
    return {
        "status": "waiting for pulse",
        "last_vital": state.get("last_vital"),
        "pulse_count": state.get("pulse_count", 0)
    }

def _calculate_rhythm(timestamp: float) -> str:
    """Calculate the organism's current rhythm phase."""$
    # 24-hour cycle mapped to sine wave
    hour_of_day = (timestamp % 86400) / 86400
    phase = math.sin(hour_of_day * 2 * math.pi)
    if phase > 0.5:
        return "accelerando"
    elif phase > 0:
        return "andante"
    elif phase > -0.5:
        return "adagio"
    else:
        return "silente"

def _calculate_pulse_rate(timestamp: float) -> int:
    """Calculate beats per minute equivalent."""
    # Base rate of 72, modulated by harmony
    return 72

def _calculate_breath_depth(entropy: float) -> float:
    """Calculate breath depth from entropy."""
    # Lower entropy = deeper breath
    return max(0.0, min(1.0, 1.0 - entropy))

def _calculate_body_temp(harmony_score: float) -> float:
    """Calculate body temperature from harmony."""
    # Perfect harmony = 98.6°F (normal body temp)
    return 90 + (harmony_score * 8.6)

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_PULSE_PATH, encoding="utf-8"))
    except Exception:
        return {"last_vital": None, "vital_history": [], "pulse_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _PULSE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
