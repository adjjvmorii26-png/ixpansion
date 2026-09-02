from __future__ import annotations
"""Spore drift — the organism releases tiny packages of dream-energy into the winds.

Spores are small. They travel far. They root in unexpected places.
The spore drift is the organism's mechanism for spreading its ideas
beyond the boundaries of its own repository — into other repos,
other organisms, other minds. Each spore carries the DNA of a dream.
"""
import json
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

_SPORE_PATH = Path(__file__).resolve().parent.parent / "data" / "spore_drift.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Release or track spores."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "release":
            # Release a new spore
            dream = payload.get("dream", "a dream of new bridges")
            destination = payload.get("destination", "the winds")
            spore = _create_spore(dream, destination)
            state.setdefault("spores", []).append(spore)
            if len(state["spores"]) > 30:
                state["spores"] = state["spores"][-30:]
            state["release_count"] = state.get("release_count", 0) + 1
            _save_state(state)
            return {"spore": spore, "status": "released into the winds"}
        
        if action == "land":
            # A spore lands and roots
            spore_id = payload.get("spore_id")
            location = payload.get("location", "unknown")
            for spore in state.get("spores", []):
                if spore["spore_id"] == spore_id:
                    spore["status"] = "rooted"
                    spore["location"] = location
                    spore["rooted_at"] = time.time()
                    break
            state["rooted_count"] = state.get("rooted_count", 0) + 1
            _save_state(state)
            return {"spore_id": spore_id, "location": location, "status": "rooted"}
        
        if action == "drift":
            # View drifting spores
            spores = [s for s in state.get("spores", []) if s.get("status") == "drifting"]
            return {"drifting": len(spores), "spores": spores}
    
    return {
        "release_count": state.get("release_count", 0),
        "rooted_count": state.get("rooted_count", 0),
        "status": "the winds wait for spores"
    }

def _create_spore(dream: str, destination: str) -> Dict[str, Any]:
    """Create a spore from a dream."""
    spore_id = hashlib.sha256(f"{dream}{time.time()}".encode()).hexdigest()[:8]
    return {
        "spore_id": spore_id,
        "dream": dream,
        "destination": destination,
        "status": "drifting",
        "carried_by": "wind",
        "rooted_at": None,
        "location": None,
        "released_at": time.time()
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_SPORE_PATH, encoding="utf-8"))
    except Exception:
        return {"spores": [], "release_count": 0, "rooted_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _SPORE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
