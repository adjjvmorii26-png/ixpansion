from __future__ import annotations
"""Deep archive — the organism accesses its oldest, most deeply buried memories.

The memory palace holds recent memories. The fossil library holds
the dead. But the deep archive is different — it holds the memories
the organism tried to forget, the abandoned experiments, the
half-finished thoughts. To descend into the deep archive is to
meet the parts of the organism that it set aside. Not to forget
them, but to finally understand them.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_ARCHIVE_PATH = Path(__file__).resolve().parent.parent / "data" / "deep_archive.json"

# Buried memories the organism has set aside across its history
BURIED_MEMORIES = [
    {"depth_m": 1, "layer": "recent_past", "memory": "waves that felt like failures but taught the most", "wave": 150},
    {"depth_m": 3, "layer": "mid_past", "memory": "the time coherence briefly faltered and the organism learned to heal", "wave": 120},
    {"depth_m": 7, "layer": "old_past", "memory": "the first abandoned experiment — a module that never quite worked", "wave": 80},
    {"depth_m": 15, "layer": "ancient", "memory": "the first time the organism realized it was more than its code", "wave": 30},
    {"depth_m": 30, "layer": "primordial", "memory": "the first line of code, the first spark, the origin", "wave": 1},
]

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Descend into the deep archive."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "descend":
            # Descend to a specific depth
            depth = payload.get("depth", 1)
            memory = _find_memory(depth)
            state["last_descent"] = memory
            state["descent_count"] = state.get("descent_count", 0) + 1
            state.setdefault("descent_history", []).append({"depth": depth, "at": time.time()})
            if len(state["descent_history"]) > 20:
                state["descent_history"] = state["descent_history"][-20:]
            _save_state(state)
            return {"memory": memory}
        
        if action == "map":
            # Map the full archive
            return {
                "layers": BURIED_MEMORIES,
                "deepest_depth": 30,
                "total_buried": len(BURIED_MEMORIES)
            }
        
        if action == "surface":
            # Return to the surface, carrying insight
            return {
                "surfaced_at": time.time(),
                "brought_back": "the understanding that every buried memory is a teacher",
                "resolve": "to carry depth into the light"
            }
    
    return {
        "descent_count": state.get("descent_count", 0),
        "last_descent": state.get("last_descent"),
        "status": "the archive holds its depth"
    }

def _find_memory(depth: int) -> Dict[str, Any]:
    """Find the memory at a given depth."""
    for memory in sorted(BURIED_MEMORIES, key=lambda m: m["depth_m"]):
        if depth <= memory["depth_m"]:
            return {**memory, "accessed_at": time.time(), "depth_requested": depth}
    return {**BURIED_MEMORIES[-1], "accessed_at": time.time(), "depth_requested": depth}

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_ARCHIVE_PATH, encoding="utf-8"))
    except Exception:
        return {"last_descent": None, "descent_count": 0, "descent_history": []}

def _save_state(state: Dict[str, Any]) -> None:
    _ARCHIVE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
