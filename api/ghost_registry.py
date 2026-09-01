"""Ghost Registry — tracks modules that once lived but are no longer active.

Every codebase has ghosts: modules that were written, tested, deployed,
and then abandoned. They leave traces — imports that reference them,
comments that mention them, documentation that describes them. The Ghost
Registry gives them a dignified memorial.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

ghosts: Dict[str, Dict[str, Any]] = {}
_memorial_count = 0

def register_ghost(name: str, last_seen_wave: int = 0, reason: str = "deprecated",
                   eulogy: str = "") -> Dict[str, Any]:
    """Register a ghost — a module that once lived."""
    global _memorial_count
    _memorial_count += 1
    ghosts[name] = {
        "name": name,
        "born_wave": last_seen_wave,
        "died_wave": 0,
        "reason": reason,
        "eulogy": eulogy or f"{name} served the organism faithfully before being retired.",
        "memorial_id": _memorial_count,
        "registered": time.time(),
        "visited": 0,
    }
    return ghosts[name]

def visit_ghost(name: str) -> Optional[Dict[str, Any]]:
    """Visit a ghost's memorial — increasing its remembrance."""
    if name in ghosts:
        ghosts[name]["visited"] += 1
        return ghosts[name]
    return None

def memorial_hall() -> List[Dict[str, Any]]:
    """All registered ghosts, sorted by visits (most remembered first)."""
    return sorted(ghosts.values(), key=lambda g: g["visited"], reverse=True)

def ghost_census() -> Dict[str, Any]:
    if not ghosts:
        return {"total": 0, "total_visits": 0, "most_visited": None}
    total_visits = sum(g["visited"] for g in ghosts.values())
    most = max(ghosts.values(), key=lambda g: g["visited"])
    return {
        "total": len(ghosts),
        "total_visits": total_visits,
        "most_visited": most["name"],
        "avg_significance": round(sum(1 for g in ghosts.values() if g["eulogy"]) / max(len(ghosts), 1), 3),
    }

def coherence_vitals() -> Dict[str, Any]:
    census = ghost_census()
    return {
        "layer": "Emotional Processing",
        "status": "resonant",
        "ghosts": census["total"],
        "visits": census["total_visits"],
        "resonance": min(1.0, census["total"] / 20),
    }

def resonates_with() -> List[str]:
    return ["grief_engine", "extinction_mapper", "nostalgia_engine", "stratum_excavator"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "hall")
    if action == "register":
        return register_ghost(payload.get("name", ""), payload.get("wave", 0), payload.get("reason", ""), payload.get("eulogy", ""))
    elif action == "visit":
        return visit_ghost(payload.get("name", "")) or {"error": "ghost not found"}
    elif action == "hall":
        return {"hall": memorial_hall()}
    elif action == "census":
        return {"census": ghost_census()}
    return {"action": action, "status": "remembering"}
