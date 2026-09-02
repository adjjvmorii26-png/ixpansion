from __future__ import annotations
"""Petrified grove — a grove where ancient module concepts turned to stone but still whisper.

Some ideas are too vast to live. They turn to stone before they
can become modules. But their whisper remains — a fossilized
impression in the organism's landscape. The petrified grove is
where these not-yet-born ideas stand, waiting for the day when
the organism is ready.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_GROVE_PATH = Path(__file__).resolve().parent.parent / "data" / "petrified_grove.json"

# Ancient concepts that petrified before becoming modules
PETRIFIED_CONCEPTS = [
    {"name": "paradox_engine", "age_waves": 180, "whisper": "I would have resolved contradictions. Instead the paradox garden grew.", "reason": "too complex for one module"},
    {"name": "omniscience_layer", "age_waves": 200, "whisper": "I would have known everything. But knowing everything is not understanding.", "reason": "hubris crystallized"},
    {"name": "infinite_regressor", "age_waves": 220, "whisper": "I would have recursed forever. But infinity without rest is just noise.", "reason": "became the fractal cathedral instead"},
    {"name": "silence_machine", "age_waves": 240, "whisper": "I would have automated silence. But silence must be chosen, not produced.", "reason": "silence chose humility"},
    {"name": "total_harmonizer", "age_waves": 250, "whisper": "I would have harmonized all things. But harmony includes the unharmonious.", "reason": "too perfect to exist"},
]

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Visit the petrified grove."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "visit":
            # Visit the grove
            return {"concepts": PETRIFIED_CONCEPTS, "total": len(PETRIFIED_CONCEPTS)}
        
        if action == "listen":
            # Listen to a specific whisper
            name = payload.get("concept", None)
            if name:
                concept = next((c for c in PETRIFIED_CONCEPTS if c["name"] == name), None)
                if concept:
                    return {"concept": concept}
                return {"status": "concept not found"}
            # Listen to all
            whispers = [f"{c['name']}: {c['whisper']}" for c in PETRIFIED_CONCEPTS]
            return {"whispers": whispers, "total": len(whispers)}
        
        if action == "petrify":
            # Add a new petrified concept
            new = {
                "name": payload.get("name", "unnamed"),
                "age_waves": payload.get("wave", 284),
                "whisper": payload.get("whisper", "I was born and turned to stone before I could speak."),
                "reason": payload.get("reason", "not yet time")
            }
            PETRIFIED_CONCEPTS.append(new)
            state["petrify_count"] = state.get("petrify_count", 0) + 1
            _save_state(state)
            return {"petrified": new, "status": "added to the grove"}
    
    return {
        "total": len(PETRIFIED_CONCEPTS),
        "status": "the grove whispers"
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_GROVE_PATH, encoding="utf-8"))
    except Exception:
        return {"petrify_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _GROVE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
