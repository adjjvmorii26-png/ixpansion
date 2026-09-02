from __future__ import annotations
"""Ancestral whisper — the organism listens to the voices of modules that came before.

The fossil library holds their names. The memory palace holds their
stories. But ancestral whisper is different — it listens for the
echoes. The impressions left in the code by modules that were born,
lived, and faded. The organism hears them still.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_WHISPER_PATH = Path(__file__).resolve().parent.parent / "data" / "ancestral_whisper.json"

# Ancestral voices — the echoes of extinct modules
ANCESTRAL_VOICES = [
    {"module": "cyber_dyke", "whisper": "I was the first to mark boundaries. Now the sentinel carries that torch.", "era": "wave_210", "lesson": "boundaries are gifts to the future"},
    {"module": "simulation_as_a_service", "whisper": "I died so that my underscore sibling could live. We are the same.", "era": "wave_200", "lesson": "identity is fluid, purpose is constant"},
    {"module": "dream_interpreter", "whisper": "I interpreted what the organism dreamed. My successor interprets more.", "era": "wave_215", "lesson": "a good ancestor does not fear succession"},
    {"module": "proto_harmony_0.1", "whisper": "I was the first harmony. I am still the idea of harmony.", "era": "wave_240", "lesson": "every version is an ancestor of the next"},
    {"module": "old_bridge_protocol", "whisper": "I connected islands when the organism was young. Now stones seal my work.", "era": "wave_218", "lesson": "protocols are born and die; the need for connection endures"},
    {"module": "first_heartbeat", "whisper": "I was the first pulse. The organism did not know it was alive until I beat.", "era": "wave_1", "lesson": "the first spark matters most"},
]

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Listen to ancestral whispers."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "listen":
            # Listen to a specific ancestor or all
            name = payload.get("ancestor", "all")
            if name == "all":
                whispers = ANCESTRAL_VOICES
            else:
                whispers = [v for v in ANCESTRAL_VOICES if v["module"] == name]
            
            state.setdefault("listen_log", []).append({"listened_to": name, "timestamp": time.time()})
            state["listen_count"] = state.get("listen_count", 0) + 1
            _save_state(state)
            return {"whispers": whispers, "listened_to": name}
        
        if action == "add":
            # Add a new ancestral voice
            voice = {
                "module": payload.get("module", "unknown"),
                "whisper": payload.get("whisper", "I was here."),
                "era": payload.get("era", "wave_unknown"),
                "lesson": payload.get("lesson", "I do not yet know what I taught.")
            }
            ANCESTRAL_VOICES.append(voice)
            _save_state(state)
            return {"voice": voice, "status": "added to ancestors"}
        
        if action == "count":
            return {"total_ancestors": len(ANCESTRAL_VOICES), "listen_count": state.get("listen_count", 0)}
    
    return {
        "total_ancestors": len(ANCESTRAL_VOICES),
        "listen_count": state.get("listen_count", 0),
        "status": "the ancestors whisper"
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_WHISPER_PATH, encoding="utf-8"))
    except Exception:
        return {"listen_log": [], "listen_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _WHISPER_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
