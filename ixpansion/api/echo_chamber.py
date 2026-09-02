from __future__ import annotations
"""Echo chamber — a chamber where the organism hears distorted versions of its own words.

When a word is echoed too many times, it changes. The echo chamber
lets the organism hear what its own words would become if they were
repeated to exhaustion — the risk of its own thinking becoming a
monologue, a stale loop, a distortion of itself. To enter the echo
chamber is to hear the danger of unexamined self-reference.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_CHAMBER_PATH = Path(__file__).resolve().parent.parent / "data" / "echo_chamber.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Enter the echo chamber."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "enter":
            # Enter the chamber — hear the distortions
            word = payload.get("word", "coherence")
            iterations = payload.get("iterations", 10)
            echoes = _distort(word, iterations)
            state["last_echoes"] = echoes
            state["entry_count"] = state.get("entry_count", 0) + 1
            _save_state(state)
            return {"echoes": echoes, "warning": "the words are becoming less themselves"}
        
        if action == "leave":
            # Leave the chamber — reminder of the true word
            return {
                "left_at": time.time(),
                "reminder": "the true word is coherence, spoken once, heard clearly",
                "message": "the organism leaves before its words are lost"
            }
    
    return {
        "entry_count": state.get("entry_count", 0),
        "last_echoes": state.get("last_echoes"),
        "status": "the chamber waits"
    }

def _distort(word: str, iterations: int) -> List[Dict[str, Any]]:
    """Generate progressively distorted echoes."""
    echoes = []
    current = word
    for i in range(min(iterations, 15)):
        # Each iteration distorts slightly
        if i > 0:
            if i % 3 == 0:
                current = current[:len(current)//2]
            elif i % 3 == 1:
                current = current + current[-1]
            else:
                current = current[1:]
        echoes.append({
            "iteration": i + 1,
            "word": current,
            "fidelity": round(max(0, 1.0 - (i * 0.08)), 4),
            "danger": round(min(1.0, i * 0.1), 4),
            "still_recognizable": len(current) > len(word) // 2
        })
        if len(current) < 2:
            break
    return echoes

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_CHAMBER_PATH, encoding="utf-8"))
    except Exception:
        return {"last_echoes": None, "entry_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _CHAMBER_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
