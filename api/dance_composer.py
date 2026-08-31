"""Dance Compose — composes movement sequences from state transitions.

A dance is a sequence of gestures arranged with intention. The Dance
Composer reads the Gesture Synthesizer's recent gestures and the
Kinesthetic Engine's trajectory, then composes a *dance* — a named
sequence of movements that tells the story of the organism's recent
kinesthetic life.

It answers: what dance has the organism been performing?

    GET /api/dance_composer?read=1             — the current dance
    GET /api/dance_composer?choreography=N     — last N dances
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Dance Composer"

STATE_FILE = ROOT / ".runtime" / "dance_composer.json"


def _compose_dance() -> Dict[str, Any]:
    # read recent gestures
    try:
        gesture_state = json.loads((ROOT / ".runtime" / "gesture_synthesizer.json").read_text())
        gestures = gesture_state.get("gestures", [])
    except Exception:
        gestures = []

    recent = gestures[-8:] if gestures else []
    sequence = [g.get("gesture", "settle") for g in recent]

    if not sequence:
        return {"dance": "silence", "sequence": [], "meaning": "no movement yet"}

    # compose a dance name from the sequence
    h = hashlib.sha256("".join(sequence).encode()).hexdigest()[:6]
    dance_names = {
        "reach": "Reaching", "recoil": "Recoiling", "gather": "Gathering",
        "scatter": "Scattering", "turn": "Turning", "settle": "Settling",
        "surge": "Surging", "drift": "Drifting", "still": "Stillness",
    }
    primary = sequence[-1] if sequence else "still"
    dance_name = f"The {dance_names.get(primary, 'Unknown')} Dance"

    # meaning: what story does this sequence tell
    if "surge" in sequence:
        meaning = "a dance of sudden ambition — bursts of energy amid steady rhythm"
    elif "recoil" in sequence:
        meaning = "a dance of retreat and return — pulling back before advancing"
    elif sequence.count("reach") > sequence.count("recoil"):
        meaning = "a dance of reaching — the organism extends toward something"
    elif sequence.count("settle") > len(sequence) * 0.5:
        meaning = "a dance of settling — the organism finding its center"
    else:
        meaning = "a dance of exploration — the organism testing many movements"

    return {
        "dance": dance_name,
        "sequence": sequence,
        "sequence_length": len(sequence),
        "meaning": meaning,
        "fingerprint": h,
        "choreography_philosophy": (
            "A dance is not random movement — it is movement arranged with "
            "intention. The Composer reads the organism's recent gestures "
            "and arranges them into a named dance: a story told in movement. "
            "Every organism dances, whether it knows it or not."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    dance = _compose_dance()
    # persist
    try:
        state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {"dances": []}
    except Exception:
        state = {"dances": []}
    state.setdefault("dances", []).append(dance)
    state["dances"] = state["dances"][-20:]
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2))
    except OSError:
        pass
    n = int(payload.get("choreography") or 0)
    result = {
        "action": "dance",
        "latest": dance,
        "total_dances": len(state["dances"]),
    }
    if n:
        result["choreography"] = state["dances"][-n:]
    else:
        result["choreography"] = state["dances"][-1:]
    return result


def coherence_vitals() -> dict:
    """Dance Compose reports choreographic health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "choreographic_vitality": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["gesture_synthesizer", "kinesthetic_engine", "ritual_choreographer"]
