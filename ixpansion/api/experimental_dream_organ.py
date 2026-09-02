from __future__ import annotations
"""Wave 228 experimental — The Dream Weaving Organ.

This organ dreams new islands into existence by weaving patterns
from the resonance graph and projecting them as potential islands.
It does not enact them — it only dreams.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List

_DREAM_PATH = Path(__file__).resolve().parent.parent / "data" / "dreams.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Dream new islands from resonance patterns."""
    dreams = _load_dreams()
    if payload and "pattern" in payload:
        dreams.append({
            "pattern": payload["pattern"],
            "created": time.time(),
            "active": True
        })
        _save_dreams(dreams)
    return {"dreams_count": len(dreams), "latest": dreams[-1] if dreams else None}

def _load_dreams() -> List[Dict[str, Any]]:
    try:
        return json.load(open(_DREAM_PATH, encoding="utf-8"))
    except Exception:
        return []

def _save_dreams(dreams: List[Dict[str, Any]]) -> None:
    _DREAM_PATH.write_text(json.dumps(dreams, indent=2, ensure_ascii=False))
