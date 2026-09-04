"""primefield_expander — Garden governance/interface/seed module."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "primefield_expander"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "primefield_expander.json")

PARADOX = "the guardian and the garden are one; to guard is to grow"
SPECTRUM = ["empty", "forming", "structured", "flourishing", "complete"]
WISDOM = "cultivation is the highest form of protection"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"count": 0, "actions": [], "created_at": time.time()}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action in ("validate", "display", "seed", "expand"):
        detail = payload.get("detail", "")
        state["count"] = state.get("count", 0) + 1
        state["actions"].append({"action": action, "detail": detail, "at": time.time()})
        if len(state["actions"]) > 50:
            state["actions"] = state["actions"][-50:]
        _save_state(state)
        return {"module": MODULE_NAME, "action": action, "count": state["count"]}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "count": state.get("count", 0),
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
    }


if __name__ == "__main__":
    print(json.dumps(handler(), indent=2))
