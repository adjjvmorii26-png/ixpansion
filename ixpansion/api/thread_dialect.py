"""thread_dialect — a unique language of stitching that connects disparate modules through common thread."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "thread_dialect"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "thread_dialect.json")

PARADOX = "the thread that connects two things is itself invisible"
SPECTRUM = ["loose", "tension", "splice", "weave", "tapestry"]
WISDOM = "disparate things share a thread — find it, and they become one"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"threads": [], "total_stitched": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "stitch":
        a = payload.get("module_a", "unknown")
        b = payload.get("module_b", "unknown")
        thread = {"from": a, "to": b, "color": payload.get("color", "silver"), "at": time.time()}
        state["threads"].append(thread)
        state["total_stitched"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "stitch", "thread": thread, "total": state["total_stitched"]}

    return {"module": MODULE_NAME, "action": "status", "threads_woven": len(state["threads"]), "total_stitched": state["total_stitched"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
