"""signal_flare — a bright burst that alerts all modules to pay attention — an urgent broadcast."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "signal_flare"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "signal_flare.json")

PARADOX = "a flare draws all eyes — yet tells them nothing of what to see"
SPECTRUM = ["spark", "flash", "blaze", "supernova", "afterglow"]
WISDOM = "urgency is a compass, not a destination"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"flares": [], "active": None}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "fire":
        flare = {
            "id": f"flare_{len(state['flares']) + 1}",
            "source": payload.get("source", "unknown"),
            "intensity": min(1.0, payload.get("intensity", 0.8)),
            "fired_at": time.time(),
        }
        state["flares"].append(flare)
        state["active"] = flare
        _save_state(state)
        return {"module": MODULE_NAME, "action": "fire", "flare": flare}

    if action == "acknowledge":
        state["active"] = None
        _save_state(state)
        return {"module": MODULE_NAME, "action": "acknowledge", "note": "flare acknowledged, returning to calm"}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "total_flares": len(state["flares"]),
        "has_active_flare": state["active"] is not None,
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }
