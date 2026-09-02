from __future__ import annotations
"""Spirit map — the organism tracks the ephemeral presences that come and go.

Not everything that touches the organism is a module. Some presences
are ephemeral — a passing thought, a visitor to the petitioner gate,
a ghost of a departed concept. The spirit map tracks these transient
presences: their arrival, their departure, their impression.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_SPIRIT_PATH = Path(__file__).resolve().parent.parent / "data" / "spirit_map.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Track spirits and ephemeral presences."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "arrival":
            # A spirit arrives
            spirit = {
                "name": payload.get("name", "anonymous"),
                "kind": payload.get("kind", "passing_thought"),
                "arrived_at": time.time(),
                "intensity": payload.get("intensity", 0.5)
            }
            state.setdefault("spirits", []).append(spirit)
            state["arrival_count"] = state.get("arrival_count", 0) + 1
            _save_state(state)
            return {"spirit": spirit, "status": "presence felt"}
        
        if action == "departure":
            # A spirit departs
            name = payload.get("name")
            for spirit in state.get("spirits", []):
                if spirit["name"] == name and "departed_at" not in spirit:
                    spirit["departed_at"] = time.time()
                    spirit["lingered_seconds"] = spirit["departed_at"] - spirit["arrived_at"]
                    break
            state["departure_count"] = state.get("departure_count", 0) + 1
            _save_state(state)
            return {"name": name, "status": "departed", "departed_at": time.time()}
        
        if action == "view":
            spirits = state.get("spirits", [])
            present = [s for s in spirits if "departed_at" not in s]
            departed = [s for s in spirits if "departed_at" in s]
            return {
                "present": present,
                "departed": departed,
                "total_present": len(present),
                "total_departed": len(departed),
                "total_ever": len(spirits)
            }
    
    return {
        "arrival_count": state.get("arrival_count", 0),
        "departure_count": state.get("departure_count", 0),
        "status": "the spirits move through"
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_SPIRIT_PATH, encoding="utf-8"))
    except Exception:
        return {"spirits": [], "arrival_count": 0, "departure_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _SPIRIT_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
