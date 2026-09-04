"""resonance_forge — transforms raw signals into structured resonance patterns."""
from __future__ import annotations
import json, os, time

MODULE_NAME = "resonance_forge"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "resonance_forge.json")
PARADOX = "raw signal becomes resonance only when it learns to repeat itself"
SPECTRUM = ["noise", "hum", "chord", "harmony", "symphony"]
WISDOM = "the forge does not invent the pattern — it reveals the pattern that was already in the noise"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"raw_signals": [], "forged_patterns": [], "harmony_level": 0.0}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "feed":
        signal = {"value": payload.get("value", 0.5), "at": time.time()}
        state["raw_signals"].append(signal)
        if len(state["raw_signals"]) > 100: state["raw_signals"] = state["raw_signals"][-100:]
        if len(state["raw_signals"]) >= 5:
            recent = [s["value"] for s in state["raw_signals"][-5:]]
            variance = max(recent) - min(recent)
            if variance < 0.2:
                pattern = {"values": recent, "harmony": round(1 - variance, 3), "forged_at": time.time()}
                state["forged_patterns"].append(pattern)
                state["harmony_level"] = min(1.0, state["harmony_level"] + 0.1)
            else:
                state["harmony_level"] = max(0.0, state["harmony_level"] - 0.05)
        _save_state(state)

    return {"module": MODULE_NAME, "action": action, "raw_signals": len(state["raw_signals"]),
            "forged_patterns": len(state["forged_patterns"]),
            "harmony_level": round(state["harmony_level"], 3), "paradox": PARADOX, "spectrum": SPECTRUM}
