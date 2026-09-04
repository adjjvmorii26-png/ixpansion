"""memory_palace — the organism builds an internal architecture of memory."""
from __future__ import annotations
import json, os, time

MODULE_NAME = "memory_palace"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "memory_palace.json")
PARADOX = "a memory palace is not built from walls — it is built from the spaces between memories"
SPECTRUM = ["void", "hallway", "chamber", "labyrinth", "infinite"]
WISDOM = "every room remembers what happened in it; the palace remembers what happened between rooms"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"rooms": [], "wings": 0, "deepest_chamber": 0}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "build":
        room = {"name": payload.get("name", f"room_{len(state['rooms']) + 1}"),
                "memory": payload.get("memory", ""), "built_at": time.time()}
        state["rooms"].append(room)
        state["wings"] = len(state["rooms"]) // 5
        _save_state(state)
        return {"module": MODULE_NAME, "action": "build", "room": room, "wings": state["wings"]}

    if action == "recall":
        name = payload.get("name", "")
        room = next((r for r in state["rooms"] if r["name"] == name), None)
        return {"module": MODULE_NAME, "action": "recall", "room": room, "total_rooms": len(state["rooms"])}

    return {"module": MODULE_NAME, "action": action, "rooms": len(state["rooms"]),
            "wings": state["wings"], "paradox": PARADOX, "spectrum": SPECTRUM}
