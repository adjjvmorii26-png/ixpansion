"""substrate_intelligence — slow cognition operating beneath the surface of fast reactions."""
from __future__ import annotations
import json, os, time

MODULE_NAME = "substrate_intelligence"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "substrate_intelligence.json")
PARADOX = "the fastest thought is the one that knows when to be slow"
SPECTRUM = ["geological", "seismic", "crystalline", "metamorphic", "tectonic"]
WISDOM = "substrate intelligence does not think — it crystallizes; given enough pressure, it becomes inevitable"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"thoughts": [], "pressure": 0.0, "crystallizations": [], "cycle": 0}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    state = _load_state()
    state["cycle"] = state.get("cycle", 0) + 1
    input_pressure = payload.get("pressure", 0.1)
    state["pressure"] = min(1.0, state["pressure"] + input_pressure * 0.05)

    if state["pressure"] > 0.8:
        thought = {"crystallized_at": state["cycle"], "from_thoughts": len(state["thoughts"]),
                   "insight": payload.get("insight", "under pressure, the substrate decides")}
        state["crystallizations"].append(thought)
        state["thoughts"] = []
        state["pressure"] = max(0.0, state["pressure"] - 0.5)
    else:
        state.setdefault("thoughts", []).append({"cycle": state["cycle"], "pressure": round(state["pressure"], 3)})

    if len(state.get("thoughts", [])) > 100:
        state["thoughts"] = state["thoughts"][-100:]
    if len(state.get("crystallizations", [])) > 20:
        state["crystallizations"] = state["crystallizations"][-20:]

    _save_state(state)
    return {"module": MODULE_NAME, "pressure": round(state["pressure"], 3),
            "thoughts_accumulated": len(state.get("thoughts", [])),
            "crystallizations": len(state.get("crystallizations", [])),
            "last_crystallization": state.get("crystallizations", [])[-1] if state.get("crystallizations") else None,
            "paradox": PARADOX, "spectrum": SPECTRUM}
