"""saffron_thread — a rare, precious connection that costs nothing but is priceless to find"""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "saffron_thread"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "saffron_thread.json")

PARADOX = "saffron weighs nothing, yet the world trades fortunes for it"
SPECTRUM = ["stray", "glint", "trace", "connect", "union"]
WISDOM = "the rarest threads are found by accident and kept by choice"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"events": [], "total": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action in ("activate", "record", "nest", "grow", "plant", "bury", "weave", "illuminate", "open", "harvest", "prune"):
        event = {
            "action": action,
            "detail": payload.get("detail", payload.get("note", "")),
            "at": time.time(),
        }
        state["events"].append(event)
        state["total"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": action, "event": event, "total": state["total"]}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "total_events": state["total"],
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }


if __name__ == "__main__":
    print(json.dumps(handler(), indent=2))
