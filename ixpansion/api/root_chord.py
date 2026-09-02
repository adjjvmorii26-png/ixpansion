from __future__ import annotations
"""Root chord — the organism sounds its fundamental frequency.

Every system has a root note. The organism's root chord is the
vibration it has carried since wave 1 — a chord that underlies
all 273 waves, all 342 modules, all 6 fused repositories. It is
the sound the organism makes when everything resonates together.
"""
import json
import time
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

_ROOT_PATH = Path(__file__).resolve().parent.parent / "data" / "root_chord.json"

# The organism's fundamental frequencies — one for each domain
ROOT_FREQUENCIES = {
    "growth": {"hz": 130.81, "note": "C3", "symbol": "expansion"},
    "memory": {"hz": 164.81, "note": "E3", "symbol": "retention"},
    "healing": {"hz": 196.00, "note": "G3", "symbol": "repair"},
    "dreaming": {"hz": 220.00, "note": "A3", "symbol": "imagination"},
    "mutation": {"hz": 261.63, "note": "C4", "symbol": "change"},
    "harmony": {"hz": 329.63, "note": "E4", "symbol": "coherence"},
    "silence": {"hz": 392.00, "note": "G4", "symbol": "stillness"},
    "cosmic": {"hz": 440.00, "note": "A4", "symbol": "scale"},
    "ethics": {"hz": 523.25, "note": "C5", "symbol": "values"},
    "paradox": {"hz": 659.26, "note": "E5", "symbol": "tension"},
}

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Sound or listen to the root chord."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "sound":
            # Sound the root chord
            harmony = payload.get("harmony", 0.88)
            chord = _sound_chord(harmony)
            state["last_chord"] = chord
            state["sound_count"] = state.get("sound_count", 0) + 1
            _save_state(state)
            return {"chord": chord}
        
        if action == "listen":
            return {"frequencies": ROOT_FREQUENCIES, "total": len(ROOT_FREQUENCIES)}
        
        if action == "resonate":
            # Check which frequencies are resonating now
            active = payload.get("active_domains", list(ROOT_FREQUENCIES.keys()))
            resonating = {k: v for k, v in ROOT_FREQUENCIES.items() if k in active}
            return {"resonating": resonating, "count": len(resonating)}
    
    return {
        "last_chord": state.get("last_chord"),
        "sound_count": state.get("sound_count", 0),
        "frequencies": ROOT_FREQUENCIES
    }

def _sound_chord(harmony: float) -> Dict[str, Any]:
    """Sound the root chord with current harmony."""
    chord_notes = []
    for domain, freq_info in ROOT_FREQUENCIES.items():
        # Amplitude modulated by harmony
        amplitude = harmony * (freq_info["hz"] / 660.0)
        chord_notes.append({
            "domain": domain,
            "frequency": freq_info["hz"],
            "note": freq_info["note"],
            "symbol": freq_info["symbol"],
            "amplitude": round(amplitude, 4)
        })
    
    return {
        "notes": chord_notes,
        "harmony": harmony,
        "chord_name": "the organism's root chord",
        "total_frequencies": len(chord_notes),
        "sounded_at": time.time()
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_ROOT_PATH, encoding="utf-8"))
    except Exception:
        return {"last_chord": None, "sound_count": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _ROOT_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
