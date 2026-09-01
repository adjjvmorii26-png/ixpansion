"""Memory Palace — the organism constructs spatial architectures for remembering.

Every memory is a room. Every room has walls of context, floors of sequence,
and ceilings of meaning. The palace grows as the organism accumulates experience,
and it can be navigated, searched, and remodeled.
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]

# ── Palace Architecture ──
rooms: Dict[str, Dict[str, Any]] = {}
hallways: Dict[str, List[str]] = {}
emotional_palette: Dict[str, float] = {}

def _room_id(name: str) -> str:
    return hashlib.sha256(name.encode()).hexdigest()[:12]

def _contextualize(memory: Dict[str, Any]) -> float:
    """Return a context richness score 0-1 based on metadata depth."""
    keys = ["source", "wave", "emotion", "timestamp", "connections"]
    present = sum(1 for k in keys if k in memory)
    return present / len(keys)

def add_memory(name: str, content: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Add a memory to the palace."""
    rid = _room_id(name)
    ctx = context or {}
    ctx["content"] = content
    ctx["richness"] = _contextualize(ctx)
    ctx["created"] = time.time()
    ctx["visit_count"] = 0
    rooms[rid] = {"name": name, "context": ctx}
    return {"room_id": rid, "name": name, "richness": ctx["richness"]}

def recall(memory_id: str) -> Optional[Dict[str, Any]]:
    """Recall a memory — increases visit count, returns content."""
    if memory_id in rooms:
        rooms[memory_id]["context"]["visit_count"] += 1
        return rooms[memory_id]
    return None

def search_palace(query: str) -> List[Dict[str, Any]]:
    """Search rooms by name substring."""
    results = []
    q = query.lower()
    for rid, room in rooms.items():
        if q in room["name"].lower():
            results.append({"id": rid, "name": room["name"],
                          "richness": room["context"]["richness"]})
    return results

def palace_stats() -> Dict[str, Any]:
    """Return palace statistics."""
    if not rooms:
        return {"total_rooms": 0, "avg_richness": 0, "most_visited": None}
    visits = [(r["name"], r["context"]["visit_count"]) for r in rooms.values()]
    most = max(visits, key=lambda x: x[1]) if visits else None
    avg_rich = sum(r["context"]["richness"] for r in rooms.values()) / len(rooms)
    return {
        "total_rooms": len(rooms),
        "avg_richness": round(avg_rich, 3),
        "most_visited": most[0] if most else None,
        "hallways": len(hallways),
    }

def coherence_vitals() -> Dict[str, Any]:
    stats = palace_stats()
    return {
        "layer": "Memory Architecture",
        "status": "resonant" if stats["total_rooms"] > 0 else "dormant",
        "room_count": stats["total_rooms"],
        "avg_richness": stats["avg_richness"],
        "resonance": min(1.0, stats["total_rooms"] / 100),
    }

def resonates_with() -> List[str]:
    return ["echo_index", "temporal_echo", "dream_archaeologist", "ancestor_map"]

def handler(payload: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    action = payload.get("action", "stats")
    if action == "add":
        return add_memory(payload.get("name", "unnamed"), payload.get("content", ""), payload.get("context"))
    elif action == "recall":
        return recall(payload.get("room_id", "")) or {"error": "room not found"}
    elif action == "search":
        return {"results": search_palace(payload.get("query", ""))}
    return {"action": action, "palace": palace_stats()}
