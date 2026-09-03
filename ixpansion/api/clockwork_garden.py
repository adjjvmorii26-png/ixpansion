"""clockwork_garden — mechanical plants that grow in mathematical spirals, each bloom a calculation."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "clockwork_garden"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "clockwork_garden.json")

PARADOX = "the gilded bloom is no less alive for being made of gears"
SPECTRUM = ["seed_gear", "sprout", "blossom", "golden_fruit", "silent_forest"]
WISDOM = "nature and mechanism are two dialects of the same unfolding"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"plants": [], "blooms": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "plant":
        plant = {"spiral_angle": payload.get("spiral_angle", 137.5), "gears": payload.get("gears", 12), "planted_at": time.time()}
        state["plants"].append(plant)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "plant", "plant": plant, "total_plants": len(state["plants"])}

    if action == "bloom":
        if state["plants"]:
            plant = state["plants"].pop(0)
            state["blooms"] += 1
            _save_state(state)
            return {"module": MODULE_NAME, "action": "bloom", "blossomed": plant, "total_blooms": state["blooms"]}
        return {"module": MODULE_NAME, "action": "bloom", "note": "garden empty"}

    return {"module": MODULE_NAME, "action": "status", "plants": len(state["plants"]), "total_blooms": state["blooms"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
