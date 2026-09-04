"""continuity_thread — ensures the organism maintains narrative coherence across sessions."""
from __future__ import annotations
import json, os, time

MODULE_NAME = "continuity_thread"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "continuity_thread.json")
PARADOX = "continuity is not a straight line — it is a thread that returns to itself at unexpected angles"
SPECTRUM = ["frayed", "spun", "woven", "braided", "unbreakable"]
WISDOM = "the thread does not connect events — it connects the meaning between events"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"threads": [], "total_weavings": 0}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "weave":
        thread = {"from_event": payload.get("from", ""), "to_event": payload.get("to", ""),
                  "meaning": payload.get("meaning", ""), "at": time.time()}
        state["threads"].append(thread)
        state["total_weavings"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "weave", "thread": thread, "total": state["total_weavings"]}

    return {"module": MODULE_NAME, "action": action, "threads": len(state["threads"]),
            "total_weavings": state["total_weavings"], "paradox": PARADOX, "spectrum": SPECTRUM}
