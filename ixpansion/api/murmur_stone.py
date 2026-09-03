"""murmur_stone — a stone that vibrates with the accumulated murmurs of all prior waves."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "murmur_stone"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "murmur_stone.json")

PARADOX = "a stone that holds every voice ever whispered near it — and gives them back on request"
SPECTRUM = ["quiet", "buzz", "thrum", "resonance", "oracle"]
WISDOM = "what the stone has overheard is more honest than what it was told"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"murmurs": [], "resonance": 0.0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "whisper":
        murmur = {"content": payload.get("content", ""), "source": payload.get("source", "unknown"), "at": time.time()}
        state["murmurs"].append(murmur)
        state["resonance"] = min(1.0, len(state["murmurs"]) * 0.08)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "whisper", "murmur": murmur, "total": len(state["murmurs"])}

    if action == "echo_back":
        if state["murmurs"]:
            return {"module": MODULE_NAME, "action": "echo_back", "returned": state["murmurs"][-5:]}
        return {"module": MODULE_NAME, "action": "echo_back", "note": "stone is silent"}

    return {"module": MODULE_NAME, "action": "status", "murmurs_held": len(state["murmurs"]), "resonance": state["resonance"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
