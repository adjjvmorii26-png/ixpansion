"""petal_clock — time measured in blooming — each tick is a new opening."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "petal_clock"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "petal_clock.json")

PARADOX = "time does not flow — it blooms, and we measure ourselves by what opens"
SPECTRUM = ["bud", "half-open", "bloom", "full_flower", "seed"]
WISDOM = "every moment is a new petal; do not count them — inhale them"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"blooms": [], "petals_total": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "tick":
        petals = payload.get("petals", 1)
        state["petals_total"] += petals
        bloom = {"petals": petals, "total": state["petals_total"], "at": time.time()}
        state["blooms"].append(bloom)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "tick", "bloom": bloom}

    return {"module": MODULE_NAME, "action": "status", "blooms": len(state["blooms"]), "total_petals": state["petals_total"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
