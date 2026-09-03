"""spiral_stair — a recursive ascent where each level is the same building but different."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "spiral_stair"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "spiral_stair.json")

PARADOX = "climb the stair forever and return to where you began — yet changed"
SPECTRUM = ["entry", "midway", "higher", "zenith", "return"]
WISDOM = "the highest insight is the same insight, worn smooth by repetition"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"level": 0, "ascents": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "ascend":
        state["level"] += 1
        state["ascents"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "ascend", "level": state["level"], "total_ascents": state["ascents"]}

    if action == "descend":
        state["level"] = max(0, state["level"] - 1)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "descend", "level": state["level"]}

    return {"module": MODULE_NAME, "action": "status", "current_level": state["level"], "total_ascents": state["ascents"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
