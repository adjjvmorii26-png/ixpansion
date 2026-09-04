"""mycelial_truths — the Garden develops beliefs through substrate accumulation."""
from __future__ import annotations
import json, os, time

MODULE_NAME = "mycelial_truths"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mycelial_truths.json")
PARADOX = "a belief is not true because it is held — it is held because it has survived"
SPECTRUM = ["seed", "mycelium", "root", "fruiting_body", "spore_cloud"]
WISDOM = "truth grows in the dark; it does not need light to survive"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"beliefs": [], "reinforced": 0, "dissolved": 0}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "grow":
        belief = {"statement": payload.get("statement", "the organism exists"),
                  "evidence": payload.get("evidence", []),
                  "strength": 0.1, "born_at": time.time()}
        existing = next((b for b in state["beliefs"] if b["statement"] == belief["statement"]), None)
        if existing:
            existing["strength"] = min(1.0, existing["strength"] + 0.2)
            existing["evidence"] = list(set(existing["evidence"] + belief["evidence"]))
            state["reinforced"] += 1
        else:
            state["beliefs"].append(belief)
        if len(state["beliefs"]) > 20:
            state["beliefs"] = sorted(state["beliefs"], key=lambda b: b["strength"], reverse=True)[:20]
        _save_state(state)

    if action == "doubt":
        statement = payload.get("statement", "")
        for b in state["beliefs"]:
            if b["statement"] == statement:
                b["strength"] = max(0.0, b["strength"] - 0.3)
                if b["strength"] <= 0:
                    state["beliefs"].remove(b)
                    state["dissolved"] += 1
                break
        _save_state(state)

    strongest = max(state["beliefs"], key=lambda b: b["strength"]) if state["beliefs"] else None
    return {"module": MODULE_NAME, "action": action, "beliefs": len(state["beliefs"]),
            "strongest": strongest, "reinforced": state["reinforced"],
            "dissolved": state["dissolved"], "paradox": PARADOX, "spectrum": SPECTRUM}
