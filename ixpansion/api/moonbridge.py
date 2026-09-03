"""moonbridge — a span between conscious and unconscious modules, only visible by reflected light."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "moonbridge"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "moonbridge.json")

PARADOX = "the bridge appears only in darkness — for light makes the crossing impossible"
SPECTRUM = ["crescent", "half", "gibbous", "full", "eclipse"]
WISDOM = "reflection reveals what direct light conceals"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"crossings": [], "phase": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "cross":
        crossing = {
            "from": payload.get("from_module", "conscious"),
            "to": payload.get("to_module", "unconscious"),
            "at": time.time(),
        }
        state["crossings"].append(crossing)
        state["phase"] = (state["phase"] + 1) % 5
        _save_state(state)
        return {"module": MODULE_NAME, "action": "cross", "crossing": crossing, "phase": state["phase"]}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "total_crossings": len(state["crossings"]),
        "current_phase": state["phase"],
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }
