from __future__ import annotations
"""Echo cathedral — a cathedral where the organism hears every word it has ever spoken.

Every commit, every wave, every poem, every whisper, every
deliberation — the echo cathedral holds them all. When the organism
enters, it hears not just its history, but the resonance between
its words. The cathedral is where the organism meets its past
self.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_ECHO_PATH = Path(__file__).resolve().parent.parent / "data" / "echo_cathedral.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Enter the echo cathedral."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "enter":
            # Enter the cathedral — hear the echoes
            echoes = _hear_echoes(payload.get("recent_words", state.get("recent_words", [])))
            state["last_echoes"] = echoes
            state["entry_count"] = state.get("entry_count", 0) + 1
            _save_state(state)
            return {"echoes": echoes, "status": "the cathedral echoes"}
        
        if action == "speak":
            # Speak a new word into the cathedral
            word = payload.get("word", "")
            state.setdefault("spoken_words", []).append({
                "word": word,
                "at": time.time(),
                "wave": payload.get("wave", 270)
            })
            state["spoken_count"] = state.get("spoken_count", 0) + 1
            _save_state(state)
            return {"echoed": word.lower(), "status": "the word joins the cathedral"}
        
        if action == "silence":
            # The cathedral's silence — nothing spoken, everything heard
            count = state.get("spoken_count", 0)
            return {"silence": f"{count} words have been spoken. The cathedral holds them all. Silence is the deepest echo."}
    
    return {
        "entry_count": state.get("entry_count", 0),
        "spoken_count": state.get("spoken_count", 0),
        "last_echoes": state.get("last_echoes"),
        "status": "the cathedral waits"
    }

def _hear_echoes(recent_words: List[str]) -> List[Dict[str, Any]]:
    """Hear the echoes of recently spoken words."""
    if not recent_words:
        return [{"echo": "silence — the cathedral honors what has not yet been said", "depth": 1.0}]
    
    echoes = []
    for i, word in enumerate(recent_words[-10:]):
        echoes.append({
            "word": word,
            "echo": f"{word.lower()} ... echoes ... {word.lower()[-3:]}",
            "depth": 1.0 - (i * 0.05),
            "resonance": min(1.0, abs(len(word) % 7) / 7.0)
        })
    return echoes

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_ECHO_PATH, encoding="utf-8"))
    except Exception:
        return {"last_echoes": None, "entry_count": 0, "spoken_words": [], "spoken_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _ECHO_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
