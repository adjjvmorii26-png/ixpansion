from __future__ import annotations
"""Poetic harmony — expresses organism state in poetic, meaningful forms."""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_POETIC_HARMONY_PATH = Path(__file__).resolve().parent.parent / "data" / "poetic_harmony.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate poetic expression from organism state."""
    state = _load_state()
    if payload and "state_snapshot" in payload:
        # Generate poetic lines from the state
        lines = _generate_poetry(payload["state_snapshot"])
        state["last_poem"] = lines
        state["poem_count"] = state.get("poem_count", 0) + 1
        state["poem_history"].append({
            "timestamp": time.time(),
            "lines": lines,
            "source_snapshot": payload["state_snapshot"]
        })
        # Keep history manageable
        if len(state["poem_history"]) > 20:
            state["poem_history"] = state["poem_history"][-20:]
        _save_state(state)
    return {"poem": state.get("last_poem"), "poem_count": state.get("poem_count", 0)}

def _generate_poetry(state_snapshot: Dict[str, Any]) -> str:
    """Generate poetic lines from system state."""
    lines = []
    
    # Entropy poem
    if "entropy" in state_snapshot:
        ent = state_snapshot["entropy"]
        lines.append(f"Entropy at {ent:.2f}, a river flowing through structured stone")
    
    # Harmony poem
    if "harmony_score" in state_snapshot:
        score = state_snapshot["harmony_score"]
        lines.append(f"Harmony {score:.2f}, the golden mean the organism breathes")
    
    # Modules poem
    if "module_count" in state_snapshot:
        count = state_snapshot["module_count"]
        lines.append(f"{count} living threads, the organism's many-eyed loom")
    
    # Waves poem
    if "wave_count" in state_snapshot:
        waves = state_snapshot["wave_count"]
        lines.append(f"{waves} waves logged, the organism's oceanic memory")
    
    # Fusion poem
    if "fusion_aware" in state_snapshot and state_snapshot["fusion_aware"]:
        lines.append(f"Fusion's fire, the two becoming one without loss")
    
    # Ensure at least one line
    if not lines:
        lines.append(f"The organism computes, exists, becomes")
    
    return "\n".join(lines)

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_POETIC_HARMONY_PATH, encoding="utf-8"))
    except Exception:
        return {"last_poem": None, "poem_count": 0, "poem_history": []}

def _save_state(state: Dict[str, Any]) -> None:
    _POETIC_HARMONY_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
