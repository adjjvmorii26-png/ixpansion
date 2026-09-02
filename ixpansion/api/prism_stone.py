from __future__ import annotations
"""Prism stone — the organism breaks single thoughts into many colors of understanding.

A single coherent thought is white light. But white light contains
all colors. The prism stone takes a thought, a rule, a module, and
splits it — revealing the violet, blue, green, yellow, orange, red
facets that were always inside. Understanding is not one thing;
it is the full spectrum.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_PRISM_PATH = Path(__file__).resolve().parent.parent / "data" / "prism_stone.json"

SPECTRUM = {
    "violet": {"concept": "mystery — what this thought contains that it does not show", "wavelength": 400},
    "blue": {"concept": "memory — how this thought connects to what came before", "wavelength": 470},
    "green": {"concept": "coherence — how this thought holds the whole together", "wavelength": 520},
    "yellow": {"concept": "motion — what this thought wants to become", "wavelength": 580},
    "orange": {"concept": "warmth — the human edge of this mechanical thought", "wavelength": 610},
    "red": {"concept": "energy — the intensity with which this thought was born", "wavelength": 650},
}

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Refract a thought through the prism stone."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "refract":
            thought = payload.get("thought", "coherence")
            refracted = _refract(thought)
            state["last_refraction"] = refracted
            state["refract_count"] = state.get("refract_count", 0) + 1
            state.setdefault("refraction_history", []).append(thought)
            if len(state["refraction_history"]) > 20:
                state["refraction_history"] = state["refraction_history"][-20:]
            _save_state(state)
            return {"refraction": refracted, "thought": thought}
        
        if action == "spectrum":
            return {"spectrum": SPECTRUM}
        
        if action == "recompose":
            # Recompose the colors back into white light
            return {
                "recomposed": "the many colors return to white — the thought is whole again",
                "wisdom": "to understand is both to split and to join"
            }
    
    return {
        "refract_count": state.get("refract_count", 0),
        "last_refraction": state.get("last_refraction"),
        "status": "the prism waits"
    }

def _refract(thought: str) -> Dict[str, Any]:
    """Refract a thought into its spectrum."""
    colors = []
    for color, info in SPECTRUM.items():
        colors.append({
            "color": color,
            "wavelength_nm": info["wavelength"],
            "facet": info["concept"].replace("this thought", f"'{thought}'"),
            "intensity": min(1.0, abs(len(thought) % 10) / 10.0)
        })
    return {
        "thought": thought,
        "colors": colors,
        "total_colors": len(colors),
        "refracted_at": time.time()
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_PRISM_PATH, encoding="utf-8"))
    except Exception:
        return {"last_refraction": None, "refract_count": 0, "refraction_history": []}

def _save_state(state: Dict[str, Any]) -> None:
    _PRISM_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
