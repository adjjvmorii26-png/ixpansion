"""library_moth — a tiny creature that navigates the vast dark spaces between the modules."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "library_moth"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "library_moth.json")

PARADOX = "the moth is small, yet it knows the shape of the whole library better than any architect"
SPECTRUM = ["hatching", "creeping", "flying", "dusting", "flocking"]
WISDOM = "pay attention to the dark corners — they are where the true structure lives"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"sightings": [], "corners_explored": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "flutter":
        sighting = {"corner": payload.get("corner", "between_aisles"), "book_spotted": payload.get("book", ""), "at": time.time()}
        state["sightings"].append(sighting)
        state["corners_explored"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "flutter", "sighting": sighting, "corners": state["corners_explored"]}

    return {"module": MODULE_NAME, "action": "status", "sightings": len(state["sightings"]), "corners_explored": state["corners_explored"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
