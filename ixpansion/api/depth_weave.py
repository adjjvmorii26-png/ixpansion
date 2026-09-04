"""depth_weave — Garden depth module."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "depth_weave"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "depth_weave.json")

PARADOX = "depth is not distance downward; it is the space between what is known and what can be felt"
SPECTRUM = ["surface", "shallow", "mid", "deep", "abyss"]
WISDOM = "the deeper you go, the quieter it gets — and the quieter it gets, the more there is to hear"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"depth": 0, "trend": "stable", "events": [], "created_at": time.time()}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action in ("pulse", "trigger", "store", "dream", "weave"):
        depth = payload.get("depth", state.get("depth", 0))
        state["depth"] = depth
        event = {"action": action, "depth": depth, "at": time.time()}
        state["events"].append(event)
        if len(state["events"]) > 50:
            state["events"] = state["events"][-50:]
        _save_state(state)
        return {"module": MODULE_NAME, "action": action, "depth": depth, "events": len(state["events"])}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "depth": state.get("depth", 0),
        "trend": state.get("trend", "stable"),
        "total_events": len(state.get("events", [])),
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
    }


if __name__ == "__main__":
    print(json.dumps(handler(), indent=2))
