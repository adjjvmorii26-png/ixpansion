"""easement — a gentle buffer zone between intense modules, providing rest and integration."""
from __future__ import annotations

import hashlib
import json
import os
import time

MODULE_NAME = "easement"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "easement.json")

PARADOX = "rest is not the absence of growth — it is growth in a different register"
SPECTRUM = ["stillness", "drift", "integration", "emergence", "radiance"]
WISDOM = "every great wave is followed by a quiet shore"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"intervals": [], "total_rest": 0, "latest_integration": None}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    depth = payload.get("depth", 1.0)
    state = _load_state()

    if action == "rest":
        interval = {
            "started": time.time(),
            "depth": min(1.0, depth),
            "note": payload.get("note", "quiet integration"),
        }
        state["intervals"].append(interval)
        state["total_rest"] += 1
        state["latest_integration"] = interval
        _save_state(state)
        return {"module": MODULE_NAME, "action": "rest", "interval": interval, "total_rest": state["total_rest"]}

    if action == "surface":
        if state["intervals"]:
            last = state["intervals"][-1]
            duration = time.time() - last.get("started", time.time())
            return {"module": MODULE_NAME, "action": "surface", "duration": round(duration, 2), "depth_emerged_from": last.get("depth", 0)}
        return {"module": MODULE_NAME, "action": "surface", "note": "already at surface"}

    depth_avg = (
        sum(i.get("depth", 0) for i in state["intervals"]) / max(1, len(state["intervals"]))
        if state["intervals"]
        else 0
    )
    return {
        "module": MODULE_NAME,
        "action": "status",
        "total_rest_events": state["total_rest"],
        "average_depth": round(depth_avg, 3),
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }


if __name__ == "__main__":
    print(json.dumps(handler({"action": "rest", "depth": 0.7, "note": "between wave 293 and 294"}), indent=2))
    print(json.dumps(handler(), indent=2))
