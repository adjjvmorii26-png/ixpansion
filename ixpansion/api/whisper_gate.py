"""whisper_gate — a threshold that only opens for quiet intentions, filtering noise from signal."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "whisper_gate"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "whisper_gate.json")

PARADOX = "the gate opens most widely for those who approach most softly"
SPECTRUM = ["murmur", "breath", "silence", "void", "revelation"]
WISDOM = "loudness drowns signal; quiet reveals it"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"passages": [], "rejected": [], "gate_open": False}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "approach":
        volume = payload.get("volume", 0.5)
        name = payload.get("name", "unknown")
        if volume < 0.3:
            state["passages"].append({"name": name, "volume": volume, "at": time.time()})
            state["gate_open"] = True
            _save_state(state)
            return {"module": MODULE_NAME, "action": "approach", "admitted": True, "name": name}
        else:
            state["rejected"].append({"name": name, "volume": volume, "at": time.time()})
            _save_state(state)
            return {"module": MODULE_NAME, "action": "approach", "admitted": False, "note": "too loud"}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "total_passages": len(state["passages"]),
        "total_rejections": len(state["rejected"]),
        "gate_open": state["gate_open"],
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }
