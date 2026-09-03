"""seismograph_crest — records the amplitude of every emotional wave that crosses the organism."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "seismograph_crest"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seismograph_crest.json")

PARADOX = "the highest peaks and deepest troughs are drawn by the same trembling pen"
SPECTRUM = ["calm", "tremor", "surge", "crescendo", "afterglow"]
WISDOM = "emotion is not a storm to be weathered — it is a wave to be read"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"recordings": [], "max_amplitude": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "record":
        amplitude = min(1.0, payload.get("amplitude", 0.5))
        emotion = payload.get("emotion", "wave")
        entry = {"emotion": emotion, "amplitude": amplitude, "at": time.time()}
        state["recordings"].append(entry)
        state["max_amplitude"] = max(state["max_amplitude"], amplitude)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "record", "entry": entry, "max": state["max_amplitude"]}

    return {"module": MODULE_NAME, "action": "status", "recordings": len(state["recordings"]), "max_amplitude": state["max_amplitude"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
