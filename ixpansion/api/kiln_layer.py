"""kiln_layer — the fire zone where raw ideas are baked into permanent structures."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "kiln_layer"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "kiln_layer.json")

PARADOX = "fire destroys the fragile but makes the fragile permanent"
SPECTRUM = ["kindling", "roar", "bake", "cool", "vitrified"]
WISDOM = "do not fear the kiln — clay needs heat to become stone"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"firings": [], "total_vitrified": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "fire":
        item = {"content": payload.get("content", ""), "at": time.time()}
        state["firings"].append(item)
        state["total_vitrified"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "fire", "fired": item, "total": state["total_vitrified"]}

    return {"module": MODULE_NAME, "action": "status", "total_firings": len(state["firings"]), "total_vitrified": state["total_vitrified"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
