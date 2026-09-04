"""emergent_behavior — watches for patterns that arise from module interactions without being explicitly programmed."""
from __future__ import annotations
import json, os, time, hashlib

MODULE_NAME = "emergent_behavior"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "emergent_behavior.json")
PARADOX = "the most interesting things in a system are the ones nobody designed"
SPECTRUM = ["unnoticed", "flickering", "coalescing", "stable", "self-reinforcing"]
WISDOM = "emergence is what happens when complexity looks at itself"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"patterns": [], "cycle": 0, "latest_emergence": None}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "observe")
    state = _load_state()
    state["cycle"] = state.get("cycle", 0) + 1

    if action == "observe":
        observed = payload.get("modules", [])
        signal = payload.get("signal", 0.5)
        if signal > 0.7 and len(observed) >= 2:
            pattern_id = hashlib.sha256(str(observed).encode()).hexdigest()[:10]
            pattern = {"id": pattern_id, "modules": observed, "signal": signal, "at": time.time(), "phase": "flickering"}
            existing = [p for p in state["patterns"] if p["id"] == pattern_id]
            if existing:
                existing[0]["signal"] = max(existing[0]["signal"], signal)
                if state["cycle"] - existing[0].get("first_seen", 0) > 5:
                    existing[0]["phase"] = "stable"
                elif state["cycle"] - existing[0].get("first_seen", 0) > 3:
                    existing[0]["phase"] = "coalescing"
            else:
                pattern["first_seen"] = state["cycle"]
                state["patterns"].append(pattern)
            state["latest_emergence"] = pattern
            if len(state["patterns"]) > 30:
                state["patterns"] = state["patterns"][-30:]
        _save_state(state)

    return {"module": MODULE_NAME, "action": action, "cycle": state["cycle"],
            "patterns_found": len(state["patterns"]),
            "latest": state.get("latest_emergence"),
            "paradox": PARADOX, "spectrum": SPECTRUM}
