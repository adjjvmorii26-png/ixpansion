"""wild_garlic — a pungent but useful herb that repels pests while healing the body"""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "wild_garlic"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "wild_garlic.json")

PARADOX = "nothing truly offensive is without purpose"
SPECTRUM = ["root", "scent", "shield", "medicine", "bloom"]
WISDOM = "pungency is just healing wearing a loud shirt"


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
