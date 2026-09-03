"""antler_crown — the branching decoration of an organism that has lived long enough to grow antlers."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "antler_crown"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "antler_crown.json")

PARADOX = "antlers are shed and regrown — maturity is not permanence, it is renewal"
SPECTRUM = ["fawn", "spike", "fork", "crown", "royal"]
WISDOM = "the crown grows heavier not with age but with responsibility"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"points": 0, "sheddings": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "grow":
        new_points = payload.get("points", 2)
        state["points"] += new_points
        _save_state(state)
        return {"module": MODULE_NAME, "action": "grow", "points_added": new_points, "total_points": state["points"]}

    if action == "shed":
        shed_points = state["points"]
        state["sheddings"] += 1
        state["points"] = 0
        _save_state(state)
        return {"module": MODULE_NAME, "action": "shed", "points_lost": shed_points, "sheddings": state["sheddings"]}

    return {"module": MODULE_NAME, "action": "status", "points": state["points"], "sheddings": state["sheddings"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
