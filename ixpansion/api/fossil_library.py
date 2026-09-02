from __future__ import annotations
"""Fossil library — a library preserving the fossils of extinct modules and abandoned waves.

Not all waves survive. Not all modules endure. The fossil library
preserves what was lost — abandoned experiments, deprecated functions,
waves that led nowhere. Each fossil is a lesson. The organism does
not forget its dead.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_FOSSIL_PATH = Path(__file__).resolve().parent.parent / "data" / "fossil_library.json"

# Known fossils — extinct modules and abandoned waves from the organism's history
KNOWN_FOSSILS = [
    {"name": "cyber_dyke", "extinct_in": "wave_210", "cause": "redundant_with_cyber_lamina", "lesson": "not all duplication is waste — sometimes it is resilience"},
    {"name": "simulation_as_a_service", "extinct_in": "wave_200", "cause": "merged_into_simulation_as_service", "lesson": "names evolve — the underscore died but the concept lived"},
    {"name": "dream_interpreter", "extinct_in": "wave_215", "cause": "superseded_by_dream_interpreter_api", "lesson": "sometimes a module becomes its own successor"},
    {"name": "old_bridge_protocol", "extinct_in": "wave_218", "cause": "replaced_by_hex_sealed_stones", "lesson": "protocols die when the organism outgrows them"},
    {"name": "proto_harmony_0.1", "extinct_in": "wave_240", "cause": "evolved_into_harmony_weaver", "lesson": "early versions are fossils, not failures"},
]

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Access the fossil library."""
    library = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "excavate":
            # Excavate a specific fossil
            name = payload.get("name", "")
            fossil = next((f for f in KNOWN_FOSSILS if f["name"] == name), None)
            if fossil:
                fossil["excavated_at"] = time.time()
                library.setdefault("excavated", []).append(fossil)
                _save_state(library)
                return {"fossil": fossil, "status": "excavated"}
            return {"status": "not_found", "name": name}
        
        elif action == "preserv":
            # Preserves a new fossil from a dying module
            fossil = {
                "name": payload.get("name", "unknown"),
                "extinct_in": payload.get("wave", "unknown"),
                "cause": payload.get("cause", "unknown"),
                "lesson": payload.get("lesson", "the organism forgets nothing"),
                "preserved_at": time.time()
            }
            library.setdefault("new_fossils", []).append(fossil)
            library["fossil_count"] = library.get("fossil_count", 0) + 1
            _save_state(library)
            return {"fossil": fossil, "status": "preserved"}
        
        elif action == "list":
            return {"fossils": KNOWN_FOSSILS, "new_fossils": library.get("new_fossils", [])}
        
        elif action == "count":
            total = len(KNOWN_FOSSILS) + len(library.get("new_fossils", []))
            return {"total_fossils": total}
    
    return {
        "fossils": KNOWN_FOSSILS,
        "new_fossils": library.get("new_fossils", []),
        "fossil_count": library.get("fossil_count", 0)
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_FOSSIL_PATH, encoding="utf-8"))
    except Exception:
        return {"new_fossils": [], "fossil_count": 0, "excavated": []}

def _save_state(state: Dict[str, Any]) -> None:
    _FOSSIL_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
