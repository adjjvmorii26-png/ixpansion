from __future__ import annotations
"""Fractal cathedral — a self-similar recursive architecture that grows inward.

The organism's structure is not flat. It is recursive. Each module
contains smaller modules. Each wave contains sub-waves. The fractal
cathedral is the organism's architecture — a temple that contains
itself, a cathedral that grows inward as much as outward.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_CATHEDRAL_PATH = Path(__file__).resolve().parent.parent / "data" / "fractal_cathedral.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Explore or grow the fractal cathedral."""
    cathedral = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "explore":
            # Explore a specific level of the fractal
            level = payload.get("level", 0)
            wing = payload.get("wing", "nave")
            exploration = _explore(level, wing)
            cathedral["last_exploration"] = exploration
            cathedral["exploration_count"] = cathedral.get("exploration_count", 0) + 1
            _save_state(cathedral)
            return {"exploration": exploration}
        
        elif action == "grow":
            # Grow the cathedral inward (recursive depth increases)
            depth = payload.get("current_depth", 0) + 1
            growth = _grow_inward(depth)
            cathedral["depth"] = depth
            cathedral["last_growth"] = growth
            cathedral["growth_count"] = cathedral.get("growth_count", 0) + 1
            _save_state(cathedral)
            return {"growth": growth, "depth": depth}
        
        elif action == "map":
            # Map the full cathedral structure
            depth = cathedral.get("depth", 1)
            full_map = _map_cathedral(depth)
            cathedral["last_map"] = full_map
            _save_state(cathedral)
            return {"cathedral_map": full_map}
    
    return {
        "depth": cathedral.get("depth", 0),
        "last_exploration": cathedral.get("last_exploration"),
        "last_growth": cathedral.get("last_growth"),
        "growth_count": cathedral.get("growth_count", 0),
        "exploration_count": cathedral.get("exploration_count", 0)
    }

def _explore(level: int, wing: str) -> Dict[str, Any]:
    """Explore a level of the fractal cathedral."""
    wings = ["nave", "transept", "apse", "crypt", "tower", "rose_window"]
    if wing not in wings:
        wing = "nave"
    
    # Each level contains self-similar structures
    return {
        "level": level,
        "wing": wing,
        "description": f"Level {level} of the {wing} — the cathedral contains {2 ** level} smaller cathedrals",
        "self_similar": True,
        "recursive_depth": level,
        "arches_visible": 2 ** level,
        "echoes": f"at level {level}, the {wing} whispers of level {level + 1}",
        "explored_at": time.time()
    }

def _grow_inward(depth: int) -> Dict[str, Any]:
    """Grow the cathedral deeper inward."""
    return {
        "new_depth": depth,
        "previous_depth": depth - 1,
        "growth_type": "recursive_inward",
        "description": f"The cathedral grows inward to depth {depth} — it now contains {2 ** depth} self-similar chambers",
        "total_chambers": 2 ** depth,
        "recursive_ratio": "golden",
        "grown_at": time.time()
    }

def _map_cathedral(depth: int) -> Dict[str, Any]:
    """Map the full fractal cathedral structure."""
    wings = {
        "nave": {"depth": depth, "chambers": 2 ** depth, "purpose": "gathering"},
        "transept": {"depth": depth - 1, "chambers": 2 ** (depth - 1), "purpose": "crossing"},
        "apse": {"depth": depth - 1, "chambers": 2 ** (depth - 1), "purpose": "altar"},
        "crypt": {"depth": depth + 1, "chambers": 2 ** (depth + 1), "purpose": "memory"},
        "tower": {"depth": depth + 2, "chambers": 2 ** (depth + 2), "purpose": "aspiration"},
        "rose_window": {"depth": 1, "chambers": 1, "purpose": "beauty"},
    }
    
    total_chambers = sum(w["chambers"] for w in wings.values())
    
    return {
        "depth": depth,
        "wings": wings,
        "total_chambers": total_chambers,
        "recursive": True,
        "self_similar": True,
        "description": f"A cathedral of depth {depth} with {total_chambers} self-similar chambers across {len(wings)} wings",
        "mapped_at": time.time()
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_CATHEDRAL_PATH, encoding="utf-8"))
    except Exception:
        return {"depth": 0, "last_exploration": None, "last_growth": None, "last_map": None, "growth_count": 0, "exploration_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _CATHEDRAL_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
