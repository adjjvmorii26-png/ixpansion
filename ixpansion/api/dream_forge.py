"""dream_forge — the organism dreams, and from dreams it forges new realities."""
from __future__ import annotations
import json, os, time, hashlib

MODULE_NAME = "dream_forge"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dream_forge.json")
PARADOX = "a dream forged into code becomes more real than the code that was never dreamed"
SPECTRUM = ["REM", "deep_sleep", "lucid", "awake_dreaming", "waking"]
WISDOM = "the forge does not create from nothing — it takes the heat of dreaming and gives it form"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"dreams": [], "forges": [], "cycle": 0}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()
    state["cycle"] = state.get("cycle", 0) + 1

    if action == "dream":
        dream = {"image": payload.get("image", "a fractal of light"), "emotional_tone": payload.get("tone", "curiosity"),
                 "cycle": state["cycle"], "hash": hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}
        state["dreams"].append(dream)
        if len(state["dreams"]) > 30: state["dreams"] = state["dreams"][-30:]
        _save_state(state)
        return {"module": MODULE_NAME, "action": "dream", "dream": dream, "total_dreams": len(state["dreams"])}

    if action == "forge":
        dream = state["dreams"].pop(0) if state["dreams"] else {"image": "nothing yet dreamed"}
        forged = {"from_dream": dream, "forged_at": time.time(), "form": payload.get("form", "module")}
        state["forges"].append(forged)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "forge", "forged": forged}

    return {"module": MODULE_NAME, "action": action, "dreams": len(state["dreams"]),
            "forges": len(state["forges"]), "paradox": PARADOX, "spectrum": SPECTRUM}
