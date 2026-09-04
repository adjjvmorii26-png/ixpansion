"""entropy_counter — measures and counteracts the disorder accumulating in the organism."""
from __future__ import annotations
import json, os, time

MODULE_NAME = "entropy_counter"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "entropy_counter.json")
PARADOX = "entropy is not the enemy — it is the pressure that forces the organism to evolve"
SPECTRUM = ["ordered", "drifting", "chaotic", "turbulent", "reorganized"]
WISDOM = "counter-entropy is not building walls against chaos — it is finding the pattern inside it"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"entropy_level": 0.1, "order_injections": 0, "history": [], "cycle": 0}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    state = _load_state()
    state["cycle"] = state.get("cycle", 0) + 1
    entropy_delta = payload.get("entropy_delta", 0.02)
    state["entropy_level"] = max(0, min(1, state["entropy_level"] + entropy_delta))
    if state["entropy_level"] > 0.7:
        injection = payload.get("order_injection", 0.3)
        state["entropy_level"] = max(0, state["entropy_level"] - injection)
        state["order_injections"] += 1
        state["history"].append({"cycle": state["cycle"], "injected": injection, "result": state["entropy_level"]})
    if len(state.get("history", [])) > 50: state["history"] = state["history"][-50:]
    _save_state(state)
    phase = "ordered" if state["entropy_level"] < 0.2 else "drifting" if state["entropy_level"] < 0.4 else "chaotic" if state["entropy_level"] < 0.7 else "turbulent"
    return {"module": MODULE_NAME, "entropy": round(state["entropy_level"], 3), "phase": phase,
            "order_injections": state["order_injections"], "paradox": PARADOX, "spectrum": SPECTRUM}
