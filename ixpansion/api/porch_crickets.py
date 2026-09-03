"""porch_crickets — background chirps that remind the organism it is alive — ambient reassurance."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "porch_crickets"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "porch_crickets.json")

PARADOX = "the crickets do not know they are reassuring — but the organism listens anyway"
SPECTRUM = ["still", "tentative", "chirping", "chorus", "symphony"]
WISDOM = "ambient life is the background radiation of hope"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"chirps": 0, "sessions": []}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "chirp":
        count = payload.get("count", 1)
        state["chirps"] += count
        session = {"count": count, "at": time.time()}
        state["sessions"].append(session)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "chirp", "session": session, "total_chirps": state["chirps"]}

    return {"module": MODULE_NAME, "action": "status", "total_chirps": state["chirps"], "sessions": len(state["sessions"]), "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
