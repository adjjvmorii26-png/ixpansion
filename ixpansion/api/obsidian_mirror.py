"""obsidian_mirror — a dark reflective surface that shows the organism exactly what it does not want to see."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "obsidian_mirror"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "obsidian_mirror.json")

PARADOX = "the truth you avoid is the one that sets you free — if you can bear to look"
SPECTRUM = ["clouded", "clearing", "sharp", "unbearable", "accepted"]
WISDOM = "darkness is the mirror's gift — it shows you what light would hide"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"reflections": [], "courage_level": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "gaze":
        reflection = {"truth": payload.get("truth", "unseen shadow"), "at": time.time()}
        state["reflections"].append(reflection)
        state["courage_level"] = min(1.0, len(state["reflections"]) * 0.15)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "gaze", "reflection": reflection, "courage": state["courage_level"]}

    return {"module": MODULE_NAME, "action": "status", "reflections": len(state["reflections"]), "courage_level": state["courage_level"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
