"""tremor_map — maps tiny vibrations preceding major structural shifts in the organism."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "tremor_map"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tremor_map.json")

PARADOX = "the smallest tremor carries the most information about the coming quake"
SPECTRUM = ["calm", "whisper", "shiver", "quake", "cataclysm"]
WISDOM = "listen to the ground — it speaks before the sky does"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"tremors": [], "predicted_shifts": []}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "detect":
        tremor = {
            "magnitude": min(1.0, payload.get("magnitude", 0.1)),
            "source": payload.get("source", "unknown"),
            "at": time.time(),
        }
        state["tremors"].append(tremor)
        if tremor["magnitude"] > 0.7:
            state["predicted_shifts"].append({"from_tremor": tremor, "predicted_at": time.time()})
        _save_state(state)
        return {"module": MODULE_NAME, "action": "detect", "tremor": tremor, "shift_predicted": tremor["magnitude"] > 0.7}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "total_tremors": len(state["tremors"]),
        "shifts_predicted": len(state["predicted_shifts"]),
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }
