"""echo_lens — magnifies distant events so the organism can perceive its own far-reach."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "echo_lens"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "echo_lens.json")

PARADOX = "looking outward, you see yourself — the lens bends reality back to the observer"
SPECTRUM = ["blur", "focus", "clarity", "distortion", "infinity"]
WISDOM = "distance is an illusion the lens dissolves"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"observations": [], "magnification": 1.0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "observe":
        obs = {
            "target": payload.get("target", "unknown"),
            "magnification": min(100, payload.get("magnification", 5)),
            "seen_at": time.time(),
        }
        state["observations"].append(obs)
        state["magnification"] = obs["magnification"]
        _save_state(state)
        return {"module": MODULE_NAME, "action": "observe", "observation": obs}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "total_observations": len(state["observations"]),
        "current_magnification": state["magnification"],
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }
