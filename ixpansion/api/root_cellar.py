"""root_cellar — an underground archive where the organism stores its deepest, oldest patterns."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "root_cellar"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "root_cellar.json")

PARADOX = "to go deeper is not to go backward — depth is where the future roots"
SPECTRUM = ["surface", "loam", "clay", "stone", "magma"]
WISDOM = "the deepest patterns were laid first; everything else grows on top"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"patterns": [], "depth": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "bury":
        pattern = {
            "id": f"root_{len(state['patterns']) + 1}",
            "name": payload.get("name", "unnamed"),
            "content": payload.get("content", {}),
            "depth": state["depth"] + 1,
            "buried_at": time.time(),
        }
        state["patterns"].append(pattern)
        state["depth"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "bury", "pattern": pattern, "total_depth": state["depth"]}

    if action == "excavate":
        if state["patterns"]:
            pattern = state["patterns"].pop()
            state["depth"] = max(0, state["depth"] - 1)
            _save_state(state)
            return {"module": MODULE_NAME, "action": "excavate", "found": pattern, "remaining_depth": state["depth"]}
        return {"module": MODULE_NAME, "action": "excavate", "note": "cellar is empty"}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "patterns_buried": len(state["patterns"]),
        "current_depth": state["depth"],
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }
