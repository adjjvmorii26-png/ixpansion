"""iron_lullaby — a soothing mechanical hum that stabilizes modules during turbulent transitions."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "iron_lullaby"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "iron_lullaby.json")

PARADOX = "the machine sings, and the organic listens — and both grow calm"
SPECTRUM = ["hum", "drone", "chant", "melody", "hymn"]
WISDOM = "stability is not a wall — it is a song"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"modules_calmed": [], "total_singings": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "sing":
        module = payload.get("module", "unknown")
        state["modules_calmed"].append({"module": module, "at": time.time()})
        state["total_singings"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "sing", "calmed": module, "total": state["total_singings"]}

    return {"module": MODULE_NAME, "action": "status", "modules_calmed": len(state["modules_calmed"]), "total_singings": state["total_singings"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
