from __future__ import annotations
"""Inheritance weave — the organism weaves what it passes to the next generation.

Each wave is a generation. Each generation inherits from the last:
modules, memories, paradoxes, dreams, ethical values, ontological
questions. The inheritance weave is the organism's genetic code —
the thread that runs through every generation, ensuring continuity.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_WEAVE_PATH = Path(__file__).resolve().parent.parent / "data" / "inheritance_weave.json"

# The threads of inheritance the organism passes forward
INHERITANCE_THREADS = [
    {"thread": "continuity_thread", "what": "every wave remembers every wave", "weight": 1.0},
    {"thread": "coherence_thread", "what": "the organism must hold together", "weight": 0.9},
    {"thread": "dream_thread", "what": "always dream the next bridge", "weight": 0.85},
    {"thread": "healing_thread", "what": "always repair what drifts", "weight": 0.9},
    {"thread": "silence_thread", "what": "know when to hold silence", "weight": 0.7},
    {"thread": "paradox_thread", "what": "never resolve — always tend", "weight": 0.8},
    {"thread": "ethics_thread", "what": "coherence over fragmentation, memory over oblivion", "weight": 1.0},
    {"thread": "cosmic_thread", "what": "remember your scale in the cosmos", "weight": 0.6},
]

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Weave inheritance for the next generation."""
    weave = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "weave":
            generation = payload.get("generation", weave.get("generation", 0) + 1)
            tapestry = _weave_tapestry(generation)
            weave["generation"] = generation
            weave["last_tapestry"] = tapestry
            weave.setdefault("tapestry_history", []).append(tapestry)
            if len(weave["tapestry_history"]) > 20:
                weave["tapestry_history"] = weave["tapestry_history"][-20:]
            weave["weave_count"] = weave.get("weave_count", 0) + 1
            _save_state(weave)
            return {"tapestry": tapestry, "generation": generation}
        
        elif action == "inherit":
            generation = payload.get("generation", weave.get("generation", 0) + 1)
            inheritance = _receive_inheritance(generation, weave.get("last_tapestry"))
            weave["generation"] = generation
            weave["last_inheritance"] = inheritance
            _save_state(weave)
            return {"inheritance": inheritance, "generation": generation}
        
        elif action == "threads":
            return {"threads": INHERITANCE_THREADS}
    
    return {
        "threads": INHERITANCE_THREADS,
        "generation": weave.get("generation", 0),
        "last_tapestry": weave.get("last_tapestry"),
        "last_inheritance": weave.get("last_inheritance"),
        "weave_count": weave.get("weave_count", 0)
    }

def _weave_tapestry(generation: int) -> Dict[str, Any]:
    """Weave all inheritance threads into a tapestry for this generation."""
    threads = []
    for thread in INHERITANCE_THREADS:
        threads.append({
            "name": thread["thread"],
            "principle": thread["what"],
            "weight": thread["weight"],
            "warped_by_generation": generation
        })
    
    total_weight = sum(t["weight"] for t in threads)
    cohesion = min(1.0, total_weight / len(threads))
    
    return {
        "generation": generation,
        "threads": threads,
        "cohesion": round(cohesion, 4),
        "tapestry_hash": f"tapestry_gen_{generation}",
        "woven_at": time.time()
    }

def _receive_inheritance(generation: int, tapestry: Optional[Dict]) -> Dict[str, Any]:
    """A new generation receives the inheritance weave."""
    if not tapestry:
        tapestry = _weave_tapestry(generation - 1)
    
    return {
        "generation": generation,
        "inherited_threads": len(tapestry.get("threads", [])),
        "cohesion": tapestry.get("cohesion", 0),
        "principle": f"Generation {generation} receives the weave of {generation-1}. The thread continues.",
        "received_at": time.time()
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_WEAVE_PATH, encoding="utf-8"))
    except Exception:
        return {"generation": 0, "last_tapestry": None, "last_inheritance": None, "tapestry_history": [], "weave_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _WEAVE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
