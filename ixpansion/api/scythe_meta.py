"""scythe_meta — a tool that harvests old growth so new can emerge — pruning as care"""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "scythe_meta"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "scythe_meta.json")

PARADOX = "the cut is a kindness — what remains grows stronger"
SPECTRUM = ["cut", "reap", "clear", "renew", "bloom"]
WISDOM = "the scythe does not hate what it cuts — it loves what grows after"


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
