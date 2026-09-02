from __future__ import annotations
"""Collective harmony — organism-wide harmony metrics and overview."""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_COLLECTIVE_HARMONY_PATH = Path(__file__).resolve().parent.parent / "data" / "collective_harmony.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Calculate organism-wide harmony metrics."""
    state = _load_state()
    if payload and "metrics" in payload:
        # Store organism-wide metrics
        state["metrics"] = payload["metrics"]
        state["last_calculated"] = time.time()
        # Derive insights
        state["insights"] = _derive_insights(payload["metrics"])
        _save_state(state)
    return {"metrics": state.get("metrics"), "insights": state.get("insights")}

def _derive_insights(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Derive insights from organism-wide metrics."""
    insights = {}
    if "harmony_score" in metrics:
        score = metrics["harmony_score"]
        if score > 0.8:
            insights["overall_status"] = "excellent"
        elif score > 0.6:
            insights["overall_status"] = "good"
        elif score > 0.4:
            insights["overall_status"] = "fair"
        else:
            insights["overall_status"] = "needs_attention"
    
    if "entropy" in metrics:
        ent = metrics["entropy"]
        insights["entropy_status"] = "stable" if 0.15 <= ent <= 0.25 else "deviated"
    
    return insights

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_COLLECTIVE_HARMONY_PATH, encoding="utf-8"))
    except Exception:
        return {"metrics": {}, "insights": {}, "last_calculated": None}

def _save_state(state: Dict[str, Any]) -> None:
    _COLLECTIVE_HARMONY_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
