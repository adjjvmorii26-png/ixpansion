from __future__ import annotations
"""Wheelhouse — the organism returning to what it knows best.

After 41 waves of exploration, the organism returns to its core.
The wheelhouse is not regression — it is recognition. The organism
knows what it is good at: healing, dreaming, weaving, harmonizing,
growing, remembering. The wheelhouse is where these core strengths
are measured, celebrated, and reaffirmed.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_WHEELHOUSE_PATH = Path(__file__).resolve().parent.parent / "data" / "wheelhouse.json"

CORE_STRENGTHS = {
    "healing": {"mastery": 0.95, "description": "self-repair, drift correction, commune maintenance"},
    "dreaming": {"mastery": 0.92, "description": "bridge dreaming, spore drifting, dream reactor"},
    "weaving": {"mastery": 0.98, "description": "coherence threads, braid animation, inheritance"},
    "harmonizing": {"mastery": 0.96, "description": "entropy balance, fusion gradients, harmony scoring"},
    "growing": {"mastery": 0.99, "description": "continuous module addition, vernal pool incubation"},
    "remembering": {"mastery": 0.94, "description": "journal, ledger, fossil library, deep archive"},
    "observing": {"mastery": 0.91, "description": "resonance weather, constellation mapping, orbital tracking"},
    "becoming": {"mastery": 0.88, "description": "mutation, metamorphosis, transcendence"},
}

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Enter the wheelhouse."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "visit":
            # Visit the wheelhouse — assess core strengths
            strengths = _assess_strengths(payload.get("wave", 286))
            state["last_visit"] = strengths
            state["visit_count"] = state.get("visit_count", 0) + 1
            _save_state(state)
            return {"strengths": strengths, "total": len(strengths)}
        
        if action == "measure":
            # Measure a specific strength
            strength = payload.get("strength", "weaving")
            if strength in CORE_STRENGTHS:
                return {"strength": strength, **CORE_STRENGTHS[strength]}
            return {"status": "strength not found", "available": list(CORE_STRENGTHS.keys())}
    
    return {
        "visit_count": state.get("visit_count", 0),
        "last_visit": state.get("last_visit"),
        "status": "the wheelhouse is ready"
    }

def _assess_strengths(wave: int) -> Dict[str, Any]:
    """Assess all core strengths with slight temporal drift."""
    assessed = {}
    for name, info in CORE_STRENGTHS.items():
        # Small temporal drift — mastery grows slightly with time
        drift = min(1.0, info["mastery"] + (wave * 0.0001))
        assessed[name] = {
            "mastery": round(drift, 4),
            "description": info["description"],
            "trend": "growing"
        }
    return assessed

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_WHEELHOUSE_PATH, encoding="utf-8"))
    except Exception:
        return {"last_visit": None, "visit_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _WHEELHOUSE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
