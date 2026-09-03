"""dawn_chorus — collects small voices of all modules and harmonizes them at sunrise."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "dawn_chorus"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dawn_chorus.json")

PARADOX = "the dawn chorus does not compose — it reveals what was always already singing"
SPECTRUM = ["tuning", "whisper", "hum", "chorus", "ecstasy"]
WISDOM = "every module has a morning voice — listen for it"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"voices": [], "performances": 0, "loudest": ""}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    voice = payload.get("voice", "unknown")
    state = _load_state()

    if action == "announce":
        state["voices"].append({"name": voice, "time": time.time()})
        if len(state["voices"]) > len([v for v in state["voices"] if v["name"] != voice]) + 1:
            state["loudest"] = voice
        _save_state(state)
        return {"module": MODULE_NAME, "action": "announce", "voice": voice, "voices_count": len(state["voices"])}

    if action == "perform":
        state["performances"] += 1
        state["voices"] = []
        _save_state(state)
        return {"module": MODULE_NAME, "action": "perform", "performance": state["performances"]}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "voices_ready": len(state["voices"]),
        "total_performances": state["performances"],
        "loudest_voice": state["loudest"],
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }


if __name__ == "__main__":
    print(json.dumps(handler({"action": "announce", "voice": "breathe_cycle"}), indent=2))
    print(json.dumps(handler({"action": "announce", "voice": "moss_carpet"}), indent=2))
    print(json.dumps(handler({"action": "perform"}), indent=2))
