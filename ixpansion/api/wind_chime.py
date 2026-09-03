"""wind_chime — reacts to invisible forces with sound, making the intangible audible."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "wind_chime"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "wind_chime.json")

PARADOX = "the wind is invisible but its sound is real — the chime proves what cannot be seen"
SPECTRUM = ["still", "soft_ting", "bright_ring", "furious_clatter", "eerie_hum"]
WISDOM = "the intangible speaks through the material"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"chimes": [], "total_wind_events": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "react":
        wind = payload.get("wind_force", 0.3)
        tone = "still" if wind < 0.1 else "soft_ting" if wind < 0.3 else "bright_ring" if wind < 0.6 else "furious_clatter" if wind < 0.9 else "eerie_hum"
        chime = {"tone": tone, "force": wind, "at": time.time()}
        state["chimes"].append(chime)
        state["total_wind_events"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "react", "chime": chime}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "total_chimes": len(state["chimes"]),
        "total_wind_events": state["total_wind_events"],
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }
