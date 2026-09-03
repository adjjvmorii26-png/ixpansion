"""dust_orchard — a quiet grove where entropy falls like fruit and is collected for composting."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "dust_orchard"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dust_orchard.json")

PARADOX = "what decays in the orchard feeds what blooms next season"
SPECTRUM = ["falling", "collecting", "composting", "enriching", "blooming"]
WISDOM = "entropy is not waste — it is fertilizer"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"fruit": [], "composted": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "harvest":
        item = {"type": payload.get("type", "entropy"), "mass": min(1.0, payload.get("mass", 0.3)), "at": time.time()}
        state["fruit"].append(item)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "harvest", "fruit": item, "pending": len(state["fruit"])}

    if action == "compost":
        state["composted"] += len(state["fruit"])
        state["fruit"] = []
        _save_state(state)
        return {"module": MODULE_NAME, "action": "compost", "total_composted": state["composted"]}

    return {"module": MODULE_NAME, "action": "status", "pending_fruit": len(state["fruit"]), "composted": state["composted"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
