"""fossil_fern — an ancient pattern pressed into the stone of the codebase, still legible after all time."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "fossil_fern"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fossil_fern.json")

PARADOX = "the fern died millennia ago, yet its pattern still shapes how new life grows"
SPECTRUM = ["sediment", "impression", "fossil", "stratum", "living_relic"]
WISDOM = "the oldest lines still draw the newest shapes"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"patterns": [], "preserved": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "press":
        pattern = {"name": payload.get("name", "fern"), "strata": payload.get("strata", 3), "at": time.time()}
        state["patterns"].append(pattern)
        state["preserved"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "press", "pattern": pattern, "preserved": state["preserved"]}

    return {"module": MODULE_NAME, "action": "status", "patterns_preserved": len(state["patterns"]), "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
