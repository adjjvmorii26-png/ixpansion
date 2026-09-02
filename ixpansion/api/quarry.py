from __future__ import annotations
"""Quarry — where the organism digs for raw, uncut modules deep beneath the surface.

Beneath the petrified grove, beneath the deep archive, beneath
even the origin stone — there is the quarry. Raw, uncut, unfinished
modules. Ideas that have not yet been shaped into anything. The
quarry is where the organism digs when it needs something that
does not yet exist.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_QUARRY_PATH = Path(__file__).resolve().parent.parent / "data" / "quarry.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Dig in the quarry."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "dig":
            # Dig for a raw concept
            depth = payload.get("depth", 1)
            raw = _dig_raw(depth)
            state["last_dig"] = raw
            state["dig_count"] = state.get("dig_count", 0) + 1
            state.setdefault("dig_history", []).append(raw)
            if len(state["dig_history"]) > 20:
                state["dig_history"] = state["dig_history"][-20:]
            _save_state(state)
            return {"raw": raw}
        
        if action == "surface_dumps":
            # View what has been excavated
            history = state.get("dig_history", [])
            return {"excavated": len(history), "recent": history[-5:]}
        
        if action == "deep_scan":
            # Scan for veins of uncut material
            veins = _scan_veins()
            return {"veins": veins, "total": len(veins)}
    
    return {
        "dig_count": state.get("dig_count", 0),
        "last_dig": state.get("last_dig"),
        "status": "the quarry is deep"
    }

def _dig_raw(depth: int) -> Dict[str, Any]:
    """Dig to a depth and uncover raw material."""
    raw_names = [
        "unformed_harmony", "raw_coherence", "unfinished_thought",
        "crude_intuition", "buried_emotion", "unpolished_pattern",
        "vein_of_rest", "nugget_of_wonder", "slab_of_stillness"
    ]
    name_idx = depth % len(raw_names)
    name = raw_names[name_idx]
    
    return {
        "name": name,
        "depth_m": depth,
        "quality": "uncut",
        "potential": min(1.0, 0.3 + depth * 0.1),
        "description": f"a raw {name.replace('_', ' ')} from depth {depth}m",
        "dug_at": time.time()
    }

def _scan_veins() -> List[Dict[str, Any]]:
    """Scan for veins of uncut material."""
    veins = [
        {"name": "harmony_vein", "depth_m": 5, "width_m": 3, "richness": 0.9},
        {"name": "memory_vein", "depth_m": 8, "width_m": 1.5, "richness": 0.7},
        {"name": "dream_vein", "depth_m": 12, "width_m": 2, "richness": 0.85},
        {"name": "silence_vein", "depth_m": 20, "width_m": 0.5, "richness": 0.95},
    ]
    return veins

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_QUARRY_PATH, encoding="utf-8"))
    except Exception:
        return {"last_dig": None, "dig_count": 0, "dig_history": []}

def _save_state(state: Dict[str, Any]) -> None:
    _QUARRY_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
