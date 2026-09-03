"""fog_cabinet — a misty storage space where the organism keeps things it is still deciding about."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "fog_cabinet"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fog_cabinet.json")

PARADOX = "to store something in fog is to give it time to become what it needs to be"
SPECTRUM = ["vapor", "mist", "haze", "condensation", "clarity"]
WISDOM = "not everything needs a label — some things need space"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"items": [], "resolved": []}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "store":
        item = {"content": payload.get("content", ""), "stored_at": time.time()}
        state["items"].append(item)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "store", "item": item, "pending": len(state["items"])}

    if action == "resolve":
        if state["items"]:
            item = state["items"].pop()
            item["resolved_at"] = time.time()
            state["resolved"].append(item)
            _save_state(state)
            return {"module": MODULE_NAME, "action": "resolve", "resolved": item}
        return {"module": MODULE_NAME, "action": "resolve", "note": "cabinet is clear"}

    return {"module": MODULE_NAME, "action": "status", "pending": len(state["items"]), "resolved": len(state["resolved"]), "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
