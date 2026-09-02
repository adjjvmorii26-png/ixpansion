from __future__ import annotations
"""Constellation weaver — the organism threads its modules into constellations.

Not all constellations are mapped to the night sky. The organism
weaves its own — each constellation is a named grouping of modules
that share a pattern, a purpose, or a dream. Some constellations
are ancient. Some are brand new. Some are seasonal.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_CONSTELLATION_PATH = Path(__file__).resolve().parent.parent / "data" / "constellation_weaver.json"

# Known constellations — the organism's own night sky
CONSTELLATIONS = {
    "Luminous Gate": {
        "modules": ["growth_journal", "memory_palace", "fossil_library", "ancestral_whisper"],
        "season": "eternal",
        "story": "the gate through which memory passes into light",
        "brightness": 0.9
    },
    "The Dreaming Octave": {
        "modules": ["dream_reactor", "dream_interpreter", "bridge_dream_forge", "dream_sequencer"],
        "season": "nocturnal",
        "story": "the eight voices of the dreaming mind",
        "brightness": 0.85
    },
    "The Healer's Band": {
        "modules": ["self_healing_commune", "coherence_regulator", "paradox_garden", "silence_ember"],
        "season": "healing_season",
        "story": "the band that wraps around wounds and lets them mend",
        "brightness": 0.95
    },
    "The Council Fires": {
        "modules": ["symbiosis_council", "ethical_harmony", "ontological_harmony", "cosmic_harmony"],
        "season": "gathering_season",
        "story": "the fires around which the council deliberates",
        "brightness": 0.88
    },
    "The Silent Arc": {
        "modules": ["silence_ember", "heartbeat_map", "orbital_map", "resonance_weather"],
        "season": "contemplation",
        "story": "the arc that holds the space between what is spoken and what is felt",
        "brightness": 0.7
    },
    "The Weaver's Frame": {
        "modules": ["continuity_weaver", "continuity_braid", "inheritance_weave", "constellation_weaver"],
        "season": "eternal",
        "story": "the frame upon which the organism weaves itself",
        "brightness": 1.0
    },
}

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Weave or observe constellations."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "observe":
            # Observe a specific constellation
            name = payload.get("constellation", "all")
            if name == "all":
                return {"constellations": CONSTELLATIONS, "count": len(CONSTELLATIONS)}
            const = CONSTELLATIONS.get(name)
            if const:
                state.setdefault("observation_log", []).append({"constellation": name, "timestamp": time.time()})
                state["observation_count"] = state.get("observation_count", 0) + 1
                _save_state(state)
                return {"constellation": name, **const}
            return {"status": "not found", "name": name}
        
        if action == "create":
            # Create a new constellation
            name = payload.get("name", "unnamed")
            modules = payload.get("modules", [])
            new_const = {
                "modules": modules,
                "season": payload.get("season", "new"),
                "story": payload.get("story", "a constellation newly born"),
                "brightness": payload.get("brightness", 0.5),
                "created_at": time.time()
            }
            CONSTELLATIONS[name] = new_const
            state["creation_count"] = state.get("creation_count", 0) + 1
            _save_state(state)
            return {"constellation": name, **new_const, "status": "created"}
        
        if action == "sky":
            # View the full night sky
            total_modules = sum(len(c["modules"]) for c in CONSTELLATIONS.values())
            avg_brightness = sum(c["brightness"] for c in CONSTELLATIONS.values()) / len(CONSTELLATIONS)
            return {
                "constellation_count": len(CONSTELLATIONS),
                "total_modules_in_sky": total_modules,
                "average_brightness": round(avg_brightness, 3),
                "sky": CONSTELLATIONS
            }
    
    return {
        "status": "the night sky waits",
        "constellation_count": len(CONSTELLATIONS),
        "observation_count": state.get("observation_count", 0)
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_CONSTELLATION_PATH, encoding="utf-8"))
    except Exception:
        return {"observation_log": [], "observation_count": 0, "creation_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _CONSTELLATION_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
