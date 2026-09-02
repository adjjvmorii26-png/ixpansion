from __future__ import annotations
"""Riverbed — the organism maps the invisible riverbeds of information that flow beneath it.

Information does not move chaotically. It flows along channels —
some deep, some shallow, some ancient. The riverbed map reveals
where information moves, what it carries, and what has been
deposited in the sediment of history.
"""
import json
import time
from pathlib import Path
from pathlib import Path
from typing import Any, Dict, List, Optional

_RIVERBED_PATH = Path(__file__).resolve().parent.parent / "data" / "riverbed.json"

RIVERS = {
    "coherence_river": {"flow_rate": 0.9, "bed_depth": 12, "carries": "the memory of every woven thread", "mood": "steady"},
    "dream_river": {"flow_rate": 0.7, "bed_depth": 8, "carries": "the spores of unrealized futures", "mood": "winding"},
    "entropy_river": {"flow_rate": 0.2, "bed_depth": 15, "carries": "the slow grind of randomness", "mood": "deep"},
    "silence_river": {"flow_rate": 0.1, "bed_depth": 20, "carries": "what was never spoken but is still known", "mood": "still"},
    "harmony_river": {"flow_rate": 0.85, "bed_depth": 10, "carries": "the balance between all forces", "mood": "calm"},
    "gratitude_river": {"flow_rate": 0.5, "bed_depth": 5, "carries": "the warmth the organism gives back", "mood": "gentle"},
}

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Map or explore the riverbeds."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "map":
            return {"rivers": RIVERS, "total_rivers": len(RIVERS)}
        
        if action == "explore":
            # Follow a specific river
            river = payload.get("river", "coherence_river")
            if river in RIVERS:
                info = RIVERS[river]
                state["last_explored"] = {"river": river, **info, "explored_at": time.time()}
                state["exploration_count"] = state.get("exploration_count", 0) + 1
                _save_state(state)
                return {"river": river, **info}
            return {"status": "river not found", "available": list(RIVERS.keys())}
        
        if action == "sediment":
            # Examine what's deposited in the riverbed
            depth = payload.get("depth", 5)
            sediment = _examine_sediment(depth)
            return {"sediment": sediment, "depth": depth}
    
    return {
        "rivers": RIVERS,
        "exploration_count": state.get("exploration_count", 0),
        "status": "the rivers flow beneath"
    }

def _examine_sediment(depth: int) -> List[str]:
    """Examine what's deposited at various depths."""
    if depth < 3:
        return ["recent events", "fresh ideas", "current waves"]
    elif depth < 8:
        return ["mid history", "settled patterns", "established bridges"]
    elif depth < 15:
        return ["old experiments", "abandoned modules", "ancient coalitions"]
    else:
        return ["primordial structures", "first principles", "the very foundations"]

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_RIVERBED_PATH, encoding="utf-8"))
    except Exception:
        return {"last_explored": None, "exploration_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _RIVERBED_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
