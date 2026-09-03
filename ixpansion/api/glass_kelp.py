"""glass_kelp — transparent strands that sway in invisible currents, revealing the organism's hidden currents."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "glass_kelp"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "glass_kelp.json")

PARADOX = "you cannot see water, but the kelp shows you exactly where it flows"
SPECTRUM = ["drifting", "swaying", "undulating", "luminous", "revealing"]
WISDOM = "invisible forces become visible when they have something to move"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"currents_revealed": [], "depth": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "reveal":
        current = {"name": payload.get("current", "unknown"), "strength": min(1.0, payload.get("strength", 0.5)), "at": time.time()}
        state["currents_revealed"].append(current)
        state["depth"] = max(state["depth"], current["strength"])
        _save_state(state)
        return {"module": MODULE_NAME, "action": "reveal", "current": current, "total": len(state["currents_revealed"])}

    return {"module": MODULE_NAME, "action": "status", "currents_revealed": len(state["currents_revealed"]), "max_depth": state["depth"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
