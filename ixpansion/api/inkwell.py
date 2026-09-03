"""inkwell — a reservoir of pure creative fluid that the organism dips into when words run dry."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "inkwell"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "inkwell.json")

PARADOX = "the well seems to empty as you use it, yet dips reveal it was never empty"
SPECTRUM = ["dry", "thin", "flowing", "rich", "oceanic"]
WISDOM = "creativity is not consumed by use — it is replenished by it"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"level": 1.0, "writings": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "dip":
        amount = min(1.0, payload.get("amount", 0.2))
        state["level"] = max(0.0, state["level"] - amount)
        state["writings"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "dip", "level_after": state["level"], "total_writings": state["writings"]}

    if action == "refill":
        state["level"] = min(1.0, state["level"] + payload.get("amount", 0.5))
        _save_state(state)
        return {"module": MODULE_NAME, "action": "refill", "level": state["level"]}

    return {"module": MODULE_NAME, "action": "status", "level": state["level"], "total_writings": state["writings"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
