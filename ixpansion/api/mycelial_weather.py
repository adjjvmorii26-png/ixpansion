"""mycelial_weather — the Garden's climate system: atmospheric pressure of thought, storms of contradiction, calm of consensus."""
from __future__ import annotations
import json, os, time

MODULE_NAME = "mycelial_weather"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mycelial_weather.json")
PARADOX = "the weather does not happen to the organism — the organism is the weather"
SPECTRUM = ["clear", "overcast", "drizzle", "storm", "calm_after"]
WISDOM = "every storm has a shape; learn the shape, and you can surf the disruption"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"pressure": 0.5, "temperature": 0.5, "humidity": 0.5, "phase": "clear", "fronts": [], "cycle": 0}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    state = _load_state()
    state["cycle"] = state.get("cycle", 0) + 1

    # Drift toward equilibrium
    state["pressure"] = state["pressure"] * 0.95 + 0.5 * 0.05
    state["temperature"] = state["temperature"] * 0.95 + 0.5 * 0.05
    state["humidity"] = state["humidity"] * 0.95 + 0.5 * 0.05

    # Apply inputs
    state["pressure"] = max(0, min(1, state["pressure"] + payload.get("pressure_delta", 0)))
    state["temperature"] = max(0, min(1, state["temperature"] + payload.get("temperature_delta", 0)))
    state["humidity"] = max(0, min(1, state["humidity"] + payload.get("humidity_delta", 0)))

    # Determine phase
    if state["pressure"] > 0.8 and state["temperature"] > 0.7:
        state["phase"] = "storm"
    elif state["pressure"] < 0.2:
        state["phase"] = "calm_after"
    elif state["humidity"] > 0.7:
        state["phase"] = "drizzle"
    elif state["pressure"] > 0.6 or state["temperature"] > 0.6:
        state["phase"] = "overcast"
    else:
        state["phase"] = "clear"

    # Storm fronts
    if state["phase"] == "storm" and (not state["fronts"] or state["fronts"][-1].get("phase") != "storm"):
        state["fronts"].append({"phase": "storm", "at": time.time(), "intensity": state["pressure"]})

    if len(state["fronts"]) > 30:
        state["fronts"] = state["fronts"][-30:]

    _save_state(state)
    return {"module": MODULE_NAME, "phase": state["phase"],
            "pressure": round(state["pressure"], 3), "temperature": round(state["temperature"], 3),
            "humidity": round(state["humidity"], 3), "total_fronts": len(state["fronts"]),
            "paradox": PARADOX, "spectrum": SPECTRUM}
