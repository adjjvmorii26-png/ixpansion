from __future__ import annotations
"""Murmuration map — the organism tracks the flock movements of its agents.

Like starlings that move as one without a leader, the organism's
agents flock together in emergent patterns. The murmuration map
tracks where they gather, how they shift, and what patterns emerge
when no single agent decides where the flock goes.
"""
import json
import time
import math
from pathlib import Path
from pathlib import Path
from pathlib import Path
from typing import Any, Dict, List, Optional

_MURMUR_PATH = Path(__file__).resolve().parent.parent / "data" / "murmuration_map.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Track and observe murmuration patterns."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "track":
            # Track a flock's current position
            flock = payload.get("flock", "general")
            agents = payload.get("agents", ["sentinel", "architect", "wanderer"])
            position = _calculate_flock_position(agents, time.time())
            state.setdefault("flocks", {})[flock] = {
                "position": position,
                "agents": agents,
                "tracked_at": time.time(),
                "murmuration_strength": len(agents) * 0.1
            }
            state["track_count"] = state.get("track_count", 0) + 1
            _save_state(state)
            return {"flock": flock, "position": position, "murmuration_strength": len(agents) * 0.1}
        
        if action == "observe":
            # Observe the full murmuration
            flocks = state.get("flocks", {})
            if not flocks:
                return {"status": "no flocks tracked yet"}
            total_agents = sum(len(f.get("agents", [])) for f in flocks.values())
            total_murmuration = sum(f.get("murmuration_strength", 0) for f in flocks.values())
            return {
                "flock_count": len(flocks),
                "total_agents": total_agents,
                "total_murmuration": round(total_murmuration, 2),
                "flocks": flocks
            }
        
        if action == "pattern":
            # Detect emergent patterns in the flock
            flocks = state.get("flocks", {})
            patterns = _detect_patterns(flocks)
            return {"patterns": patterns}
    
    return {
        "flock_count": len(state.get("flocks", {})),
        "track_count": state.get("track_count", 0),
        "status": "the flock is still"
    }

def _calculate_flock_position(agents: List[str], timestamp: float) -> Dict[str, Any]:
    """Calculate flock centroid from agent positions."""
    x = sum(int(a.encode().hex(), 16) % 100 for a in agents) / len(agents)
    y = sum(int(a.encode().hex(), 16) % 50 for a in agents) / len(agents)
    angle = (timestamp % 600) / 600 * 2 * math.pi
    return {"x": round(x, 2), "y": round(y, 2), "angle": round(angle, 4)}

def _detect_patterns(flocks: Dict[str, Any]) -> List[str]:
    """Detect emergent patterns in flock movements."""
    patterns = []
    for name, flock in flocks.items():
        if flock.get("murmuration_strength", 0) > 0.5:
            patterns.append(f"the {name} flock is murmuring strongly")
        if len(flock.get("agents", [])) > 5:
            patterns.append(f"the {name} flock is unusually large — emergent behavior likely")
    return patterns or ["the flocks are calm"]

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_MURMUR_PATH, encoding="utf-8"))
    except Exception:
        return {"flocks": {}, "track_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _MURMUR_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
