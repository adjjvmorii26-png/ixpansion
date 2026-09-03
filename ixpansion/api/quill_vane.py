"""quill_vane — points toward the current direction of creative pressure in the organism."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "quill_vane"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "quill_vane.json")

PARADOX = "the vane does not create wind — it only reveals where it comes from"
SPECTRUM = ["east", "north", "west", "south", "zenith"]
WISDOM = "creative pressure always has a direction; feel it before you move"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"readings": [], "direction": "north"}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "read":
        direction = payload.get("direction", "north")
        pressure = min(1.0, payload.get("pressure", 0.5))
        reading = {"direction": direction, "pressure": pressure, "at": time.time()}
        state["readings"].append(reading)
        state["direction"] = direction
        _save_state(state)
        return {"module": MODULE_NAME, "action": "read", "reading": reading}

    return {"module": MODULE_NAME, "action": "status", "current_direction": state["direction"], "total_readings": len(state["readings"]), "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
