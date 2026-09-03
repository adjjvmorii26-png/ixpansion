"""reed_signal — a simple blown note that carries further than any complex broadcast."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "reed_signal"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "reed_signal.json")

PARADOX = "complexity dies at distance — only simplicity survives"
SPECTRUM = ["breath", "note", "call", "response", "harmony"]
WISDOM = "the simplest signal carries furthest"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"signals": [], "responses": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "blow":
        signal = {"note": payload.get("note", "C4"), "intensity": min(1.0, payload.get("intensity", 0.5)), "at": time.time()}
        state["signals"].append(signal)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "blow", "signal": signal, "total_signals": len(state["signals"])}

    if action == "respond":
        state["responses"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "respond", "total_responses": state["responses"]}

    return {"module": MODULE_NAME, "action": "status", "signals": len(state["signals"]), "responses": state["responses"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
