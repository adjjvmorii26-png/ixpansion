"""vapor_trail — a fading record of where the organism has been — visible only in retrospect."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "vapor_trail"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "vapor_trail.json")

PARADOX = "the past disappears the moment you try to look at it directly — only its vapor remains"
SPECTRUM = ["trace", "contrail", "streak", "cloud", "dissipation"]
WISDOM = "memory is not a photograph — it is weather"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"trails": [], "visible_in_retrospect": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "mark":
        trail = {"event": payload.get("event", "unknown"), "at": time.time()}
        state["trails"].append(trail)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "mark", "trail": trail, "total": len(state["trails"])}

    if action == "retrospect":
        state["visible_in_retrospect"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "retrospect", "retrospective_views": state["visible_in_retrospect"]}

    return {"module": MODULE_NAME, "action": "status", "trails": len(state["trails"]), "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
