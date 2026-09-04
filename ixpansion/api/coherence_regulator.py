"""coherence_regulator — ensures the organism stays coherent even as its axioms mutate."""
from __future__ import annotations
import json, os, time

MODULE_NAME = "coherence_regulator"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "coherence_regulator.json")
PARADOX = "coherence is not the absence of contradiction — it is the ability to hold contradictions together"
SPECTRUM = ["scattered", "gathering", "aligned", "resonant", "unified"]
WISDOM = "the regulator does not eliminate chaos; it gives chaos a shape"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"score": 0.5, "drifts": [], "corrections": [], "cycle": 0}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    state = _load_state()
    state["cycle"] = state.get("cycle", 0) + 1
    coherence_input = payload.get("coherence", 0.5)
    drift = abs(coherence_input - state["score"])
    if drift > 0.3:
        state["drifts"].append({"cycle": state["cycle"], "drift": round(drift, 3), "from": state["score"], "to": coherence_input})
        correction = drift * 0.3
        state["score"] = state["score"] + (coherence_input - state["score"]) * 0.3
        state["corrections"].append({"cycle": state["cycle"], "correction": round(correction, 3)})
    else:
        state["score"] = state["score"] * 0.9 + coherence_input * 0.1
    state["score"] = max(0, min(1, state["score"]))
    if len(state.get("drifts", [])) > 50: state["drifts"] = state["drifts"][-50:]
    if len(state.get("corrections", [])) > 50: state["corrections"] = state["corrections"][-50:]
    _save_state(state)
    return {"module": MODULE_NAME, "score": round(state["score"], 3), "drifts": len(state["drifts"]),
            "corrections": len(state["corrections"]), "paradox": PARADOX, "spectrum": SPECTRUM}
