"""elm_shade — a cooling layer that lets delicate operations survive the heat of ambition."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "elm_shade"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "elm_shade.json")

PARADOX = "shade is not the absence of sun — it is the tree's gift to the understory"
SPECTRUM = ["sun", "dappled", "shade", "cool", "twilight"]
WISDOM = "what survives in shadow grows stronger than what burns in light"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"modules_shaded": [], "total_shadings": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "shade":
        module = payload.get("module", "unknown")
        state["modules_shaded"].append({"module": module, "at": time.time()})
        state["total_shadings"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "shade", "shaded": module, "total": state["total_shadings"]}

    return {"module": MODULE_NAME, "action": "status", "modules_shaded": len(state["modules_shaded"]), "total_shadings": state["total_shadings"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
