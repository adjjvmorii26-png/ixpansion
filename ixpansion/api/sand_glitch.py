"""sand_glitch — a module that runs fine but occasionally produces beautiful errors on purpose."""
from __future__ import annotations

import hashlib
import json
import os
import time

MODULE_NAME = "sand_glitch"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sand_glitch.json")

PARADOX = "an error made with intention is not a failure — it is an offering"
SPECTRUM = ["smooth", "ripple", "glitch", "beautiful_crack", "mosaic"]
WISDOM = "perfection is boring — the glitch is where beauty lives"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"runs": 0, "glitches": []}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "run":
        state["runs"] += 1
        glitch_chance = payload.get("glitch_chance", 0.3)
        seed = hashlib.sha256(f"glitch-{state['runs']}-{time.time()}".encode()).hexdigest()
        if int(seed[:4], 16) / 0xFFFF < glitch_chance:
            glitch = {"run": state["runs"], "pattern": seed[:8], "at": time.time()}
            state["glitches"].append(glitch)
            _save_state(state)
            return {"module": MODULE_NAME, "action": "run", "result": "beautiful_glitch", "glitch": glitch}
        _save_state(state)
        return {"module": MODULE_NAME, "action": "run", "result": "smooth"}

    return {"module": MODULE_NAME, "action": "status", "total_runs": state["runs"], "total_glitches": len(state["glitches"]), "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
