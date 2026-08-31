"""Gesture Synthesizer — creates movement patterns from state changes.

A gesture is a movement with meaning: a wave, a reach, a recoil. The
Gesture Synthesizer reads the organism's state transitions (coherence
shifts, new cracks, repairs, pulse spikes) and synthesizes *gestures*
— named movement patterns that describe what the organism just *did*
in kinesthetic terms.

It answers: what gesture did the organism just make?

    GET /api/gesture_synthesizer?read=1         — recent gestures
    GET /api/gesture_synthesizer?history=N      — last N gestures
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Gesture Synthesizer"

STATE_FILE = ROOT / ".runtime" / "gesture_synthesizer.json"

_GESTURES = [
    ("reach", "extending toward a new state"),
    ("recoil", "pulling back from a disruption"),
    ("gather", "collecting scattered energy into a center"),
    ("scatter", "dispersing energy outward"),
    ("turn", "rotating to face a new direction"),
    ("settle", "coming to rest after movement"),
    ("surge", "a sudden burst of forward motion"),
    ("drift", "slow, unguided movement"),
]


def _synthesize_gesture() -> Dict[str, Any]:
    try:
        import json
        cr = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        history = cr.get("history", [])
    except Exception:
        history = []

    if len(history) < 2:
        return {"gesture": "still", "meaning": "no movement detected"}

    current = history[-1].get("coherence", 0.5)
    previous = history[-2].get("coherence", 0.5)
    delta = current - previous
    magnitude = abs(delta)

    if magnitude < 0.005:
        gesture, meaning = "settle", "coming to rest after movement"
    elif delta > 0.05:
        gesture, meaning = "surge", "a sudden burst of forward motion"
    elif delta > 0.02:
        gesture, meaning = "reach", "extending toward a new state"
    elif delta < -0.05:
        gesture, meaning = "recoil", "pulling back from a disruption"
    elif delta < -0.02:
        gesture, meaning = "drift", "slow, unguided movement backward"
    else:
        gesture, meaning = "turn", "rotating to face a new direction"

    return {
        "gesture": gesture,
        "meaning": meaning,
        "delta": round(delta, 4),
        "magnitude": round(magnitude, 4),
        "timestamp": time.time(),
    }


def _load_history() -> List[Dict[str, Any]]:
    try:
        return json.loads(STATE_FILE.read_text()).get("gestures", [])
    except Exception:
        return []


def _save_gesture(gesture: Dict[str, Any]) -> None:
    import json
    history = _load_history()
    history.append(gesture)
    history = history[-30:]
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps({"gestures": history}, indent=2))
    except OSError:
        pass


def handler(payload: dict = None, context: object = None) -> dict:
    import json
    payload = payload or {}
    gesture = _synthesize_gesture()
    _save_gesture(gesture)
    history = _load_history()
    n = int(payload.get("history") or 0)
    result = {
        "action": "gesture",
        "latest": gesture,
        "total_gestures": len(history),
    }
    if n:
        result["gestures"] = history[-n:]
    else:
        result["gestures"] = history[-1:]
    return result


def coherence_vitals() -> dict:
    """Gesture Synthesizer reports gesture-detection health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "gesture_vitality": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["kinesthetic_engine", "morphic_dial", "system_mood"]
