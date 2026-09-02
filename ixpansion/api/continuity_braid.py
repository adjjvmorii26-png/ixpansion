from __future__ import annotations
"""Continuity braid — animates coherence threads across axiom mutations."""
import json
import time
from pathlib import Path
from typing import Any, Dict, List

_BRIDGE_PATH = Path(__file__).resolve().parent.parent / "data" / "continuity_braid.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Animate continuity braid state."""
    braid = _load_braid()
    if payload and "thread_id" in payload:
        # Find or create thread
        thread = next((t for t in braid.get("threads", []) if t.get("id") == payload["thread_id"]), None)
        if thread:
            thread["last_animated"] = time.time()
            if "amplitude" in payload:
                thread["amplitude"] = payload["amplitude"]
            if "phase" in payload:
                thread["phase"] = payload["phase"]
        else:
            braid.setdefault("threads", []).append({
                "id": payload["thread_id"],
                "created": time.time(),
                "amplitude": payload.get("amplitude", 1.0),
                "phase": payload.get("phase", 0.0),
                "last_animated": time.time()
            })
        _save_braid(braid)
    return {"total_threads": len(braid.get("threads", [])), "animated": payload.get("thread_id") if payload else None}

def _load_braid() -> Dict[str, Any]:
    try:
        return json.load(open(_BRIDGE_PATH, encoding="utf-8"))
    except Exception:
        return {"threads": [], "total_animations": 0}

def _save_braid(braid: Dict[str, Any]) -> None:
    _BRIDGE_PATH.write_text(json.dumps(braid, indent=2, ensure_ascii=False))
