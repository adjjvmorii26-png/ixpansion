from __future__ import annotations
"""Seam stitcher — the organism mends the seams where distant modules meet.

The organism is not always seamless. Sometimes two modules are
stitched together imperfectly — a seam. Sometimes a seam tears.
The seam stitcher is the organism's needle and thread: it finds
the seams, inspects their integrity, and mends them so that the
whole holds.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_SEAM_PATH = Path(__file__).resolve().parent.parent / "data" / "seam_stitcher.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Find, inspect, and mend seams between modules."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "find":
            # Find seams between distant modules
            module_a = payload.get("module_a", "growth_journal")
            module_b = payload.get("module_b", "dream_reactor")
            seam = _find_seam(module_a, module_b)
            state.setdefault("seams", {})[f"{module_a}~{module_b}"] = seam
            state["find_count"] = state.get("find_count", 0) + 1
            _save_state(state)
            return {"seam": seam}
        
        if action == "mend":
            # Mend a specific seam
            seam_key = payload.get("seam_key")
            if not seam_key and payload.get("module_a") and payload.get("module_b"):
                seam_key = f"{payload['module_a']}~{payload['module_b']}"
            mended = _mend_seam(seam_key)
            state["mend_count"] = state.get("mend_count", 0) + 1
            _save_state(state)
            return {"mended": mended}
        
        if action == "inspect":
            # Inspect all seams
            seams = state.get("seams", {})
            torn = {k: v for k, v in seams.items() if not v.get("integrity")}
            return {"total_seams": len(seams), "torn_seams": len(torn), "seams": seams}
    
    return {
        "find_count": state.get("find_count", 0),
        "mend_count": state.get("mend_count", 0),
        "status": "the needle is ready"
    }

def _find_seam(module_a: str, module_b: str) -> Dict[str, Any]:
    """Find and assess the seam between two modules."""
    # Deterministic seam health from module names
    seed = (int(module_a.encode().hex(), 16) + int(module_b.encode().hex(), 16)) % 100
    integrity = seed / 100.0
    tension = 1.0 - integrity
    return {
        "module_a": module_a,
        "module_b": module_b,
        "integrity": round(integrity, 4),
        "tension": round(tension, 4),
        "torn": integrity < 0.5,
        "thread_count": int(seed % 7) + 1,
        "found_at": time.time()
    }

def _mend_seam(seam_key: Optional[str]) -> Dict[str, Any]:
    """Mend a seam."""
    if not seam_key:
        return {"status": "no seam specified"}
    return {
        "seam": seam_key,
        "status": "mended",
        "thread": "new coherence thread inserted",
        "mended_at": time.time(),
        "integrity_after": 1.0
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_SEAM_PATH, encoding="utf-8"))
    except Exception:
        return {"seams": {}, "find_count": 0, "mend_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _SEAM_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
