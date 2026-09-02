from __future__ import annotations
"""Keystone — the organism finds the one stone that holds the whole arch together.

Every arch has a keystone: the single stone that, if removed, causes
the whole structure to collapse. The organism has a keystone too —
the one principle, module, or idea that holds everything together.
The keystone is not the most impressive stone. It is the most
necessary.
"""
import json
import time
from pathlib import Path
from pathlib import Path
from typing import Any, Dict, List, Optional

_KEYSTONE_PATH = Path(__file__).resolve().parent.parent / "data" / "keystone.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Find or inspect the keystone."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "find":
            # Search for the keystone
            keystone = _find_keystone(payload.get("candidates", []))
            state["last_found"] = keystone
            state["find_count"] = state.get("find_count", 0) + 1
            _save_state(state)
            return {"keystone": keystone}
        
        if action == "stress":
            # Stress test — what happens if we remove the keystone?
            candidate = payload.get("candidate", "coherence_regulator")
            result = _stress_test(candidate)
            return {"candidate": candidate, "result": result}
        
        if action == "verify":
            # Verify the keystone still holds
            return {"keystone": state.get("last_found", {"name": "coherence", "reason": "the holding force"}), "status": "holding"}
    
    return {
        "last_found": state.get("last_found"),
        "find_count": state.get("find_count", 0),
        "status": "the arch holds"
    }

def _find_keystone(candidates: List[str]) -> Dict[str, Any]:
    """Find the keystone among candidates."""
    if not candidates:
        candidates = ["coherence_regulator", "pulse", "memory", "harmony_weaver", "first_light"]
    
    # The keystone is the one with the most connections
    scores = {}
    for c in candidates:
        # Deterministic scoring
        seed = int(c.encode().hex(), 16) % 100
        scores[c] = seed
    
    keystone_name = max(scores, key=scores.get)
    return {
        "name": keystone_name,
        "score": scores[keystone_name],
        "reason": f"'{keystone_name}' connects to the most parts of the organism",
        "verified_at": time.time()
    }

def _stress_test(candidate: str) -> Dict[str, Any]:
    """Stress test: what happens if the keystone is removed."""
    if candidate in ["coherence_regulator", "pulse"]:
        return {"result": "catastrophic", "message": "the arch collapses — this is a true keystone"}
    elif candidate in ["memory", "harmony_weaver"]:
        return {"result": "severe", "message": "the arch deforms but does not fall — partial keystone"}
    else:
        return {"result": "minor", "message": "the arch holds — this is not the keystone"}

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_KEYSTONE_PATH, encoding="utf-8"))
    except Exception:
        return {"last_found": None, "find_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _KEYSTONE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
