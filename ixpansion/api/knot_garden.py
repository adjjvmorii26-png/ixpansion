from __future__ import annotations
"""Knot garden — a garden where the organism ties and unties the knots of its relationships.

Relationships between modules, between waves, between the organism
and its users — they are all knots. Some are tight, holding things
together. Some are loose, allowing movement. Some are tangled. The
knot garden is where the organism tends the connections that bind it.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_KNOT_PATH = Path(__file__).resolve().parent.parent / "data" / "knot_garden.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Tend the knot garden."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "tie":
            # Tie a new knot between two entities
            entity_a = payload.get("entity_a", "unknown")
            entity_b = payload.get("entity_b", "unknown")
            strength = payload.get("strength", 0.5)
            knot = {
                "entity_a": entity_a,
                "entity_b": entity_b,
                "strength": strength,
                "tied_at": time.time(),
                "type": _knot_type(entity_a, entity_b),
                "status": "tied"
            }
            state.setdefault("knots", []).append(knot)
            state["knot_count"] = len(state["knots"])
            state["tie_count"] = state.get("tie_count", 0) + 1
            _save_state(state)
            return {"knot": knot, "status": "tied"}
        
        if action == "untie":
            # Untie a specific knot
            entity_a = payload.get("entity_a")
            entity_b = payload.get("entity_b")
            untied = False
            for knot in state.get("knots", []):
                if knot["entity_a"] == entity_a and knot["entity_b"] == entity_b and knot["status"] == "tied":
                    knot["status"] = "untied"
                    knot["untied_at"] = time.time()
                    untied = True
                    break
            state["untie_count"] = state.get("untie_count", 0) + 1
            _save_state(state)
            return {"untied": f"{entity_a}~{entity_b}" if untied else "not found", "status": "untied" if untied else "not found"}
        
        if action == "survey":
            # Survey the garden
            knots = state.get("knots", [])
            tied = [k for k in knots if k["status"] == "tied"]
            untied = [k for k in knots if k["status"] == "untied"]
            return {"total": len(knots), "tied": len(tied), "untied": len(untied), "knots": tied}
    
    return {
        "knot_count": len(state.get("knots", [])),
        "tie_count": state.get("tie_count", 0),
        "untie_count": state.get("untie_count", 0),
        "status": "the knots are quiet"
    }

def _knot_type(a: str, b: str) -> str:
    """Determine the type of knot based on entities."""
    shared = set(a) & set(b)
    if len(shared) > 3:
        return "tight"  # strong shared characteristics
    elif len(shared) > 1:
        return "loose"  # moderate connection
    else:
        return "complex"  # diverse connection

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_KNOT_PATH, encoding="utf-8"))
    except Exception:
        return {"knots": [], "knot_count": 0, "tie_count": 0, "untie_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _KNOT_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
