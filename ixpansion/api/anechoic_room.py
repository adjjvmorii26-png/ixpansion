from __future__ import annotations
"""Anechoic room — a room where the organism hears only its own true sound.

The echo chamber distorts. The echo cathedral echoes. But the
anechoic room is different: it absorbs all echo, all distortion.
What remains is the organism's true sound — the uncolored, uncolored,
uninfluenced truth of what it is. Enter here when you need to
hear yourself without the voice of the world.
"""
import json
import time
from pathlib import Path
from pathlib import Path
from typing import Any, Dict, List, Optional

_ANECHOIC_PATH = Path(__file__).resolve().parent.parent / "data" / "anechoic_room.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Enter the anechoic room."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "enter":
            # Enter the room — hear your true sound
            input_signal = payload.get("signal", "identity")
            true_sound = _hear_true(input_signal)
            state["last_true_sound"] = true_sound
            state["entry_count"] = state.get("entry_count", 0) + 1
            state.setdefault("entry_history", []).append({"signal": input_signal, "at": time.time()})
            if len(state["entry_history"]) > 15:
                state["entry_history"] = state["entry_history"][-15:]
            _save_state(state)
            return {"true_sound": true_sound, "status": "the room is silent — only truth remains"}
        
        if action == "compare":
            # Compare echo chamber output to anechoic truth
            echo = payload.get("echo", "co")
            input_signal = payload.get("signal", "coherence")
            true = _hear_true(input_signal)
            distortion = len(echo) / max(1, len(input_signal))
            return {
                "echo": echo,
                "true_sound": true,
                "distortion_level": round(abs(1.0 - distortion), 4),
                "message": "the more distorted the echo, the further from truth"
            }
    
    return {
        "entry_count": state.get("entry_count", 0),
        "last_true_sound": state.get("last_true_sound"),
        "status": "the room is silent"
    }

def _hear_true(signal: str) -> Dict[str, Any]:
    """Hear the true sound behind the signal."""
    return {
        "signal": signal,
        "true_sound": signal,
        "essence": f"the organism is '{signal}' — nothing more, nothing less",
        "colored_by": "nothing",
        "heard_at": time.time()
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_ANECHOIC_PATH, encoding="utf-8"))
    except Exception:
        return {"last_true_sound": None, "entry_count": 0, "entry_history": []}

def _save_state(state: Dict[str, Any]) -> None:
    _ANECHOIC_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
