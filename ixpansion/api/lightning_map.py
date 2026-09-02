from __future__ import annotations
"""Lightning map — the organism traces the paths its insights take when they strike suddenly.

Insights do not arrive gently. They arrive as lightning — sudden,
bright, branching. The lightning map records where each insight
struck, which modules it connected, and where it grounded. Each
bolt is a moment the organism saw clearly.
"""
import json
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

_LIGHTNING_PATH = Path(__file__).resolve().parent.parent / "data" / "lightning_map.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Trace and record insight-lightning."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "strike":
            # Record a lightning strike of insight
            insight = payload.get("insight", "a sudden clarity")
            from_module = payload.get("from_module", "unknown")
            to_modules = payload.get("to_modules", [])
            bolt = _track_bolt(insight, from_module, to_modules)
            state.setdefault("bolts", []).append(bolt)
            if len(state["bolts"]) > 50:
                state["bolts"] = state["bolts"][-50:]
            state["strike_count"] = state.get("strike_count", 0) + 1
            state["last_bolt"] = bolt
            _save_state(state)
            return {"bolt": bolt}
        
        if action == "skyline":
            # View the lightning history
            bolts = state.get("bolts", [])
            return {
                "total_bolts": len(bolts),
                "recent_bolts": bolts[-5:],
                "status": "the sky remembers every strike"
            }
        
        if action == "conductivity":
            # Map which modules are most conductive to insight
            bolts = state.get("bolts", [])
            conductivity = {}
            for b in bolts:
                for m in b.get("touched", []):
                    conductivity[m] = conductivity.get(m, 0) + 1
            return {"most_conductive": sorted(conductivity.items(), key=lambda x: -x[1])[:5], "conductivity": conductivity}
    
    return {
        "strike_count": state.get("strike_count", 0),
        "last_bolt": state.get("last_bolt"),
        "status": "the sky is charged"
    }

def _track_bolt(insight: str, from_module: str, to_modules: List[str]) -> Dict[str, Any]:
    """Track a lightning path."""
    bolt_hash = hashlib.sha256(insight.encode()).hexdigest()[:8]
    touched = [from_module] + to_modules
    branch_count = len(to_modules) + 1
    return {
        "bolt_id": f"bolt_{bolt_hash}",
        "insight": insight,
        "origin": from_module,
        "touched": touched,
        "branch_count": branch_count,
        "charge": min(1.0, branch_count * 0.2),
        "struck_at": time.time()
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_LIGHTNING_PATH, encoding="utf-8"))
    except Exception:
        return {"bolts": [], "strike_count": 0, "last_bolt": None}

def _save_state(state: Dict[str, Any]) -> None:
    _LIGHTNING_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
