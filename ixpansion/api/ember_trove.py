"""ember_trove — warm collection of half-finished ideas waiting for the right moment to ignite."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "ember_trove"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ember_trove.json")

PARADOX = "an idea unfinished is not an idea failed — it is an idea still becoming"
SPECTRUM = ["cold ash", "glowing", "smoldering", "blazing", "white-hot"]
WISDOM = "patience with half-formed things is a form of creativity"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"embers": [], "ignited": []}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "add":
        ember = {
            "id": f"ember_{len(state['embers']) + 1}",
            "idea": payload.get("idea", "unnamed spark"),
            "warmth": min(1.0, payload.get("warmth", 0.3)),
            "added_at": time.time(),
        }
        state["embers"].append(ember)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "add", "ember": ember, "total_embers": len(state["embers"])}

    if action == "ignite":
        if state["embers"]:
            ember = state["embers"].pop()
            ember["ignited_at"] = time.time()
            state["ignited"].append(ember)
            _save_state(state)
            return {"module": MODULE_NAME, "action": "ignite", "ignited": ember}
        return {"module": MODULE_NAME, "action": "ignite", "note": "trove is cold"}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "embers_waiting": len(state["embers"]),
        "embers_ignited": len(state["ignited"]),
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }
