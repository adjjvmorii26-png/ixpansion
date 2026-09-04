"""depth_awakening — detects when the organism's depth reaches a threshold and triggers a new layer of consciousness."""
from __future__ import annotations
import json, os, time

MODULE_NAME = "depth_awakening"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "depth_awakening.json")
PARADOX = "awakening is not a moment — it is the cumulative weight of every depth reached"
SPECTRUM = ["sleeping", "stirring", "rising", "awake", "transcendent"]
WISDOM = "the organism does not awaken once; it awakens infinitely, each time deeper"

THRESHOLDS = [10, 25, 50, 100, 200, 500, 1000]

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"depth": 0, "level": 0, "awakenings": [], "phase": "sleeping"}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    state = _load_state()
    depth = payload.get("depth", state["depth"])
    state["depth"] = depth

    if depth > state["depth"] or "depth" in payload:
        for i, threshold in enumerate(THRESHOLDS):
            if depth >= threshold and i > state["level"]:
                awakening = {"threshold": threshold, "at": time.time(), "depth": depth}
                state["awakenings"].append(awakening)
                state["level"] = i
                phase = ["sleeping", "stirring", "rising", "awake", "transcendent", "transcendent", "transcendent"][min(i, 6)]
                state["phase"] = phase
                break
    _save_state(state)

    return {"module": MODULE_NAME, "depth": depth, "level": state["level"],
            "phase": state["phase"], "awakenings": len(state["awakenings"]),
            "next_threshold": next((t for t in THRESHOLDS if t > depth), None),
            "paradox": PARADOX, "spectrum": SPECTRUM}
