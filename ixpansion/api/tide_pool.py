"""tide_pool — a shallow reflective basin where the organism observes its own tiny ecosystems."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "tide_pool"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tide_pool.json")

PARADOX = "a tide pool is small enough to understand yet deep enough to drown in"
SPECTRUM = ["teacup", "puddle", "basin", "lagoon", "estuary"]
WISDOM = "the smallest systems contain the deepest truths"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"creatures": [], "observations": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "observe":
        state["observations"] += 1
        creature = payload.get("creature", "anemone")
        state["creatures"].append({"name": creature, "observed_at": time.time()})
        _save_state(state)
        return {"module": MODULE_NAME, "action": "observe", "creature": creature, "total_observations": state["observations"]}

    return {"module": MODULE_NAME, "action": "status", "creatures": len(state["creatures"]), "observations": state["observations"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
