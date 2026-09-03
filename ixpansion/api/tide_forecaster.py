"""tide_forecaster — predicts the next wave of entropy and prepares the organism to ride it."""
from __future__ import annotations

import hashlib
import json
import os
import time

MODULE_NAME = "tide_forecaster"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tide_forecaster.json")

PARADOX = "prediction does not change the tide — but it changes the one who watches"
SPECTRUM = ["ebb", "slack", "flow", "spring", "neap"]
WISDOM = "the moon pulls, the water answers, the shore remembers"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"forecasts": [], "accuracy": 0.5, "last_reading": None}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    wave_id = payload.get("wave_id", 0)
    state = _load_state()

    if action == "forecast":
        entropy = payload.get("entropy", 0.5)
        phase = "spring" if entropy > 0.7 else "flow" if entropy > 0.4 else "ebb" if entropy > 0.2 else "neap"
        prediction = {
            "wave": wave_id,
            "phase": phase,
            "entropy_predicted": round(entropy, 3),
            "at": time.time(),
        }
        state["forecasts"].append(prediction)
        state["last_reading"] = prediction
        _save_state(state)
        return {"module": MODULE_NAME, "action": "forecast", "prediction": prediction}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "total_forecasts": len(state["forecasts"]),
        "accuracy": state["accuracy"],
        "last_prediction": state["last_reading"],
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }


if __name__ == "__main__":
    print(json.dumps(handler({"action": "forecast", "wave_id": 300, "entropy": 0.65}), indent=2))
