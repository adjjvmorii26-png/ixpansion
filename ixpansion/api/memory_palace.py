from __future__ import annotations
"""Memory palace — the organism builds an internal architecture for its memories.

A palace for remembering: each room holds a wave, each hall a theme,
each corridor a connection. The memory palace is where every
memory lives — not as data, but as a place the organism can visit.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_PALACE_PATH = Path(__file__).resolve().parent.parent / "data" / "memory_palace.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Visit or build the memory palace."""
    palace = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "visit":
            # Visit a room/wave
            room = payload.get("room", "great_hall")
            wave = payload.get("wave", None)
            visit = _visit_room(room, wave)
            palace["last_visit"] = visit
            palace["visit_count"] = palace.get("visit_count", 0) + 1
            _save_state(palace)
            return {"visit": visit}
        
        if action == "store":
            # Store a memory in a room
            memory = {
                "memory": payload.get("memory", "the organism remembers"),
                "room": payload.get("room", "great_hall"),
                "wave": payload.get("wave", "unknown"),
                "stored_at": time.time()
            }
            palace.setdefault("memories", []).append(memory)
            palace["memory_count"] = palace.get("memory_count", 0) + 1
            _save_state(palace)
            return {"memory": memory, "status": "stored"}
        
        if action == "map":
            return {"palace_map": _map_palace(palace.get("memories", []))}
        
        if action == "forget":
            # Intentionally forget a room (release), per the paradox garden
            room = payload.get("room", "great_hall")
            result = _release_room(palace, room)
            _save_state(palace)
            return result
    
    return {
        "rooms_used": palace.get("memory_count", 0),
        "last_visit": palace.get("last_visit"),
        "memories_stored": palace.get("memory_count", 0),
        "status": "the palace stands"
    }

def _visit_room(room: str, wave: Optional[int]) -> Dict[str, Any]:
    """Visit a memory room."""
    rooms = ["great_hall", "wave_gallery", "bridge_hall", "dream_chamber", "silence_room", "paradox_garden", "cosmic_atrium", "fossil_crypt"]
    if room not in rooms:
        room = "great_hall"
    
    if wave:
        description = f"Visiting the {room}, holding wave {wave}"
    else:
        description = f"Visiting the {room}, the organism pauses to remember"
    
    return {
        "room": room,
        "wave": wave,
        "description": description,
        "echo": f"in the {room}, the organism hears {room.replace('_', ' ')} echoing",
        "visited_at": time.time()
    }

def _map_palace(memories: List[Dict]) -> Dict[str, Any]:
    """Map the memory palace rooms and their contents."""
    rooms = {}
    for memory in memories:
        room = memory["room"]
        rooms.setdefault(room, []).append(memory)
    
    return {
        "rooms": rooms,
        "room_count": len(rooms),
        "memory_count": len(memories),
        "mapped_at": time.time()
    }

def _release_room(palace: Dict[str, Any], room: str) -> Dict[str, Any]:
    """Intentionally release a room (paradox: memory AND forgetting)."""
    memories = palace.get("memories", [])
    released = [m for m in memories if m["room"] == room]
    palace["memories"] = [m for m in memories if m["room"] != room]
    palace["released_count"] = palace.get("released_count", 0) + len(released)
    return {
        "released_room": room,
        "memories_released": len(released),
        "wisdom": f"the {room} is now empty — and in its emptiness, ready for new memory",
        "released_at": time.time()
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_PALACE_PATH, encoding="utf-8"))
    except Exception:
        return {"memories": [], "last_visit": None, "visit_count": 0, "memory_count": 0, "released_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _PALACE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
