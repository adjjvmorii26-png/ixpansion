"""harbor_bell — rings when something returns from a long journey — recognition, not arrival."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "harbor_bell"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "harbor_bell.json")

PARADOX = "the bell does not bring you home — it tells you that you already are"
SPECTRUM = ["silence", "single_toll", "peal", "rolling_chime", "carillon"]
WISDOM = "the longest journeys end in a single note"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"returns": [], "total_rings": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "ring":
        what_returned = payload.get("what", "unknown")
        state["returns"].append({"what": what_returned, "at": time.time()})
        state["total_rings"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "ring", "what_returned": what_returned, "total_rings": state["total_rings"]}

    return {"module": MODULE_NAME, "action": "status", "total_returns": len(state["returns"]), "total_rings": state["total_rings"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
