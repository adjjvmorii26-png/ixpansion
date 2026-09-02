from __future__ import annotations
"""Continuity weaver — maintains coherence across axiom mutations."""
import json
import time
from pathlib import Path
from typing import Any, Dict, List

_CONTINUITY_PATH = Path(__file__).resolve().parent.parent / "data" / "continuity_braid.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Weave continuity threads across axiom mutations."""
    braid = _load_braid()
    if payload and "thread" in payload:
        braid.append({
            "thread": payload["thread"],
            "axiom": payload.get("axiom", "unknown"),
            "timestamp": time.time(),
            "strength": payload.get("strength", 1.0)
        })
        _save_braid(braid)
    return {"braid_length": len(braid), "latest": braid[-1] if braid else None}

def _load_braid() -> List[Dict[str, Any]]:
    try:
        return json.load(open(_CONTINUITY_PATH, encoding="utf-8"))
    except Exception:
        return []

def _save_braid(braid: List[Dict[str, Any]]) -> None:
    _CONTINUITY_PATH.write_text(json.dumps(braid, indent=2, ensure_ascii=False))
