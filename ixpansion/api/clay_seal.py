"""clay_seal — a stamp pressed into wet clay that dries into immutable contract between modules."""
from __future__ import annotations

import hashlib
import json
import os
import time

MODULE_NAME = "clay_seal"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "clay_seal.json")

PARADOX = "a seal is broken to prove it was once whole"
SPECTRUM = ["wet", "pressed", "drying", "fired", "permanent"]
WISDOM = "a contract written in clay is more binding than one written in ink"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"seals": [], "broken": []}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "seal":
        a = payload.get("module_a", "A")
        b = payload.get("module_b", "B")
        terms = payload.get("terms", "mutual aid")
        seal_id = hashlib.sha256(f"{a}-{b}-{terms}".encode()).hexdigest()[:8]
        seal = {"id": seal_id, "between": [a, b], "terms": terms, "at": time.time()}
        state["seals"].append(seal)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "seal", "seal": seal}

    if action == "break":
        if state["seals"]:
            seal = state["seals"].pop()
            state["broken"].append(seal)
            _save_state(state)
            return {"module": MODULE_NAME, "action": "break", "broken": seal}
        return {"module": MODULE_NAME, "action": "break", "note": "no seals to break"}

    return {"module": MODULE_NAME, "action": "status", "active_seals": len(state["seals"]), "broken_seals": len(state["broken"]), "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
