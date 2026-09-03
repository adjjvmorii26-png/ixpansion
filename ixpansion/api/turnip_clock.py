"""turnip_clock — a peasant's timekeeper — measures time by what grows, not what ticks."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "turnip_clock"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "turnip_clock.json")

PARADOX = "the turnip knows nothing of clocks, yet it tells time better than any pendulum"
SPECTRUM = ["seed", "sprout", "bulb", "harvest", "next_season"]
WISDOM = "clocks measure what passes; gardens measure what arrives"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"plantings": [], "harvests": []}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "plant":
        plant = {"name": payload.get("name", "turnip"), "season": payload.get("season", "spring"), "at": time.time()}
        state["plantings"].append(plant)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "plant", "planted": plant, "total_plantings": len(state["plantings"])}

    if action == "harvest":
        if state["plantings"]:
            plant = state["plantings"].pop(0)
            plant["harvested_at"] = time.time()
            state["harvests"].append(plant)
            _save_state(state)
            return {"module": MODULE_NAME, "action": "harvest", "harvested": plant}
        return {"module": MODULE_NAME, "action": "harvest", "note": "nothing planted yet"}

    return {"module": MODULE_NAME, "action": "status", "plantings": len(state["plantings"]), "harvests": len(state["harvests"]), "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
