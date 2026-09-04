"""morii_weaver — Garden organ module."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "morii_weaver"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "morii_weaver.json")

PARADOX = "what is measured becomes real; what is real resists measurement"
SPECTRUM = ["dormant", "stirring", "active", "resonant", "radiant"]
WISDOM = "every module is a mirror; the organism sees itself in each one"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"events": [], "total": 0, "created_at": time.time()}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action in ("pulse", "capture", "weave", "act", "synthesize", "govern"):
        event = {"action": action, "at": time.time(), "detail": payload.get("detail", "")}
        state["events"].append(event)
        state["total"] += 1
        if len(state["events"]) > 50:
            state["events"] = state["events"][-50:]
        _save_state(state)
        return {"module": MODULE_NAME, "action": action, "total": state["total"]}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "total_events": state["total"],
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
    }


if __name__ == "__main__":
    print(json.dumps(handler(), indent=2))
