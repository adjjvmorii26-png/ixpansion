from __future__ import annotations
"""Temporal harmony — tracks harmony states across time, enabling learning and pattern recognition."""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_TEMPORAL_HARMONY_PATH = Path(__file__).resolve().parent.parent / "data" / "temporal_harmony.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Record and analyze temporal harmony patterns."""
    state = _load_state()
    if payload and "harmony_entry" in payload:
        # Add entry to history with timestamp
        entry = {
            "entropy": payload.get("entropy"),
            "gradient": payload.get("gradient"),
            "harmony_score": payload.get("harmony_score"),
            "timestamp": time.time(),
            "wave": payload.get("wave", "unknown")
        }
        state["history"].append(entry)
        # Keep history manageable
        if len(state["history"]) > 100:
            state["history"] = state["history"][-100:]
        
        # Calculate patterns
        state["patterns"] = _analyze_patterns(state["history"])
        state["last_recorded"] = time.time()
        _save_state(state)
    return {"total_entries": len(state.get("history", [])), "patterns": state.get("patterns", {})}

def _analyze_patterns(history: List[Dict]) -> Dict[str, Any]:
    """Analyze patterns in harmony history."""
    if not history:
        return {"trend": "stable", "average_score": 0, "frequency": {}}
    
    scores = [e.get("harmony_score", 0) for e in history]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Trend: improving, declining, or stable
    if len(scores) >= 10:
        first_quarter = sum(scores[:len(scores)//4]) / (len(scores)//4) if len(scores)//4 > 0 else 0
        last_quarter = sum(scores[-len(scores)//4:]) / (len(scores)//4) if len(scores)//4 > 0 else 0
        if last_quarter > first_quarter * 1.05:
            trend = "improving"
        elif last_quarter < first_quarter * 0.95:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    # Frequency of gradient states
    gradient_freq = {}
    for e in history:
        g = e.get("gradient")
        if g:
            g_key = str(sorted(g.items()))
            gradient_freq[g_key] = gradient_freq.get(g_key, 0) + 1
    
    return {
        "trend": trend,
        "average_score": round(avg_score, 4),
        "gradient_frequency": gradient_freq,
        "entry_count": len(history)
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_TEMPORAL_HARMONY_PATH, encoding="utf-8"))
    except Exception:
        return {"history": [], "patterns": {}, "last_recorded": None}

def _save_state(state: Dict[str, Any]) -> None:
    _TEMPORAL_HARMONY_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
