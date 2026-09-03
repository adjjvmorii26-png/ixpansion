"""stone_choir — ancient modules sing in harmony, their voices resonating through deep time."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "stone_choir"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "stone_choir.json")

PARADOX = "even stone can sing if given enough time and resonance"
SPECTRUM = ["rumble", "hum", "chord", "anthem", "elegy"]
WISDOM = "the choir that has existed longest does not need a conductor"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"voices": [], "harmony_level": 0, "last_performance": None}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    voice = payload.get("voice", "unknown")
    state = _load_state()

    if action == "join":
        state["voices"].append({"name": voice, "joined": time.time()})
        state["harmony_level"] = min(1.0, len(state["voices"]) * 0.12)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "join", "voice": voice, "voices": len(state["voices"]), "harmony": state["harmony_level"]}

    if action == "sing":
        state["last_performance"] = time.time()
        resonance = min(1.0, state["harmony_level"] + 0.1)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "sing", "voices": len(state["voices"]), "resonance": resonance}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "voices": len(state["voices"]),
        "harmony_level": state["harmony_level"],
        "last_performance": state["last_performance"],
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }


if __name__ == "__main__":
    print(json.dumps(handler({"action": "join", "voice": "easement"}), indent=2))
    print(json.dumps(handler({"action": "sing"}), indent=2))
