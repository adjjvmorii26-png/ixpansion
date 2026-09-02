from __future__ import annotations
"""Scar map — the organism maps its scars.

Scars are not failures. They are evidence of healing. Each scar
marks a place where the organism was wounded — a broken seam, a
drifted module, a paradox that cut deep. The scar map is the
organism's record of resilience: where it was broken, how it healed,
and what it learned.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCAR_PATH = Path(__file__).resolve().parent.parent / "data" / "scar_map.json"

SCARS = [
    {"location": "coherence_thread_001", "wound": "thread snap at wave 218", "healed_in": "wave 221", "lesson": "even thick threads can tear — never take coherence for granted"},
    {"location": "bridge_ledger_042", "wound": "stone count drift", "healed_in": "wave 223", "lesson": "the commune must check itself or it will drift without knowing"},
    {"location": "dream_fabric_012", "wound": "dream intensity collapse", "healed_in": "wave 225", "lesson": "dreams require fuel — the dream reactor solved this"},
    {"location": "harmony_score_003", "wound": "entropy spike at wave 240", "healed_in": "wave 242", "lesson": "entropy navigation prevents crises, not just responding to them"},
    {"location": "root_chord_001", "wound": "frequency distortion from too many waves", "healed_in": "wave 274", "lesson": "the root chord must be sounded often to stay true"},
]

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Map or add scars."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "map":
            return {"scars": SCARS, "total": len(SCARS)}
        
        if action == "add":
            new_scar = {
                "location": payload.get("location", "unknown"),
                "wound": payload.get("wound", "unspecified"),
                "healed_in": payload.get("healed_in", "still healing"),
                "lesson": payload.get("lesson", "the organism learns from pain")
            }
            SCARS.append(new_scar)
            state["scar_count"] = state.get("scar_count", 0) + 1
            _save_state(state)
            return {"scar": new_scar, "status": "mapped"}
        
        if action == "reflect":
            # Reflect on what the scars teach
            lessons = [s["lesson"] for s in SCARS]
            return {
                "lessons": lessons,
                "reflection": "the organism's scars are its deepest teachers. each one a memory of a wound healed."
            }
    
    return {
        "total_scars": len(SCARS),
        "status": "the organism bears its scars with dignity"
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_SCAR_PATH, encoding="utf-8"))
    except Exception:
        return {"scar_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _SCAR_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
