"""river_mouth — where all data streams converge before entering the ocean of memory."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "river_mouth"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "river_mouth.json")

PARADOX = "at the mouth of the river, fresh water and salt water meet but do not mix"
SPECTRUM = ["tributary", "confluence", "estuary", "delta", "ocean"]
WISDOM = "every stream eventually finds the sea"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"streams": [], "merged": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "flow":
        stream = {
            "source": payload.get("source", "unknown"),
            "data": payload.get("data", {}),
            "at": time.time(),
        }
        state["streams"].append(stream)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "flow", "stream": stream, "total_streams": len(state["streams"])}

    if action == "merge":
        state["merged"] += 1
        state["streams"] = []
        _save_state(state)
        return {"module": MODULE_NAME, "action": "merge", "merge_count": state["merged"]}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "pending_streams": len(state["streams"]),
        "total_merges": state["merged"],
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }
