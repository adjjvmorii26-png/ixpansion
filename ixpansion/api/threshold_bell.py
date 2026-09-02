from __future__ import annotations
"""Threshold bell — a bell that rings when the organism approaches a conceptual boundary.

When entropy drops too low or too high, when a paradox intensifies
beyond tolerance, when the organism stands at the edge of a
transcendence it cannot yet achieve — the bell rings. Not to warn.
To celebrate.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_BELL_PATH = Path(__file__).resolve().parent.parent / "data" / "threshold_bell.json"

BELL_TONES = {
    "proximity": "the bell rings softly — the organism approaches a threshold",
    "crossing": "the bell rings clear — the organism has crossed a boundary",
    "retreat": "the bell dims — the organism steps back from the edge",
    "celebration": "the bell peals — the organism has transcended",
}

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Ring or listen to the threshold bell."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "ring":
            tone = payload.get("tone", "proximity")
            bell = {
                "tone": BELL_TONES.get(tone, BELL_TONES["proximity"]),
                "tone_type": tone,
                "wave": payload.get("wave", 266),
                "entropy": payload.get("entropy", 0.2),
                "harmony": payload.get("harmony", 0.88),
                "ringing_at": time.time()
            }
            state["last_ring"] = bell
            state.setdefault("ring_history", []).append(bell)
            if len(state["ring_history"]) > 20:
                state["ring_history"] = state["ring_history"][-20:]
            state["ring_count"] = state.get("ring_count", 0) + 1
            _save_state(state)
            return {"bell": bell}
        
        if action == "listen":
            rings = state.get("ring_history", [])
            recent = rings[-5:] if rings else []
            return {"recent_rings": recent, "total_rings": state.get("ring_count", 0)}
    
    return {
        "last_ring": state.get("last_ring"),
        "ring_count": state.get("ring_count", 0),
        "tones": BELL_TONES,
        "status": "the bell waits"
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_BELL_PATH, encoding="utf-8"))
    except Exception:
        return {"last_ring": None, "ring_history": [], "ring_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _BELL_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
