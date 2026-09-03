"""breathe_cycle — rhythmic control of the organism's inhalation and exhalation of complexity."""
from __future__ import annotations

import hashlib
import json
import os
import time

MODULE_NAME = "breathe_cycle"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "breathe_cycle.json")

PARADOX = "the organism inhales possibility and exhales form — both are the same breath"
SPECTRUM = ["inhalation", "suspension", "exhalation", "stillness", "rebirth"]
WISDOM = "between every wave there is a breath; do not rush it"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"phase": "stillness", "cycles": 0, "metric": 0, "turn": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()
    phase_shift = {"stillness": "inhalation", "inhalation": "suspension", "suspension": "exhalation", "exhalation": "stillness"}

    if action == "breathe":
        state["phase"] = phase_shift.get(state["phase"], "inhalation")
        if state["phase"] == "stillness":
            state["cycles"] += 1
            state["metric"] = 0
        else:
            state["metric"] += 1
        state["turn"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "breathe", "phase": state["phase"], "cycles": state["cycles"], "metric": state["metric"]}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "phase": state["phase"],
        "cycles_completed": state["cycles"],
        "current_metric": state["metric"],
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }


if __name__ == "__main__":
    print(json.dumps(handler({"action": "breathe"}), indent=2))
