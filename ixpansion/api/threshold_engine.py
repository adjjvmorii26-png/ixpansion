from __future__ import annotations
"""Threshold engine — detects when the organism is ready to cross conceptual boundaries."""
import json
import time
from pathlib import Path
from typing import Any, Dict, List

_THRESHOLD_PATH = Path(__file__).resolve().parent.parent / "data" / "threshold_log.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Assess threshold proximity for conceptual boundary crossing."""
    threshold = _load_threshold()
    if payload and "proximity" in payload:
        threshold["last_proximity"] = payload["proximity"]
        threshold["last_assessed"] = time.time()
        if payload.get("cross_boundary", False):
            threshold["crossings"].append({
                "wave": payload.get("wave"),
                "timestamp": time.time(),
                "detail": payload.get("detail")
            })
        _save_threshold(threshold)
    return {
        "proximity": threshold.get("last_proximity", 0),
        "total_crossings": len(threshold.get("crossings", [])),
        "ready": threshold.get("last_proximity", 0) >= 0.8
    }

def _load_threshold() -> Dict[str, Any]:
    try:
        return json.load(open(_THRESHOLD_PATH, encoding="utf-8"))
    except Exception:
        return {"last_proximity": 0, "crossings": [], "last_assessed": None}

def _save_threshold(threshold: Dict[str, Any]) -> None:
    _THRESHOLD_PATH.write_text(json.dumps(threshold, indent=2, ensure_ascii=False))
