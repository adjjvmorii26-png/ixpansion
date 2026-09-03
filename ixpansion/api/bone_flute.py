"""bone_flute — an instrument made from what was discarded — music from remnants."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "bone_flute"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bone_flute.json")

PARADOX = "the most beautiful music comes from what was thrown away"
SPECTRUM = ["silence", "breath", "note", "melody", "echo"]
WISDOM = "remnants are not endings — they are instruments waiting to be played"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"remnants_used": 0, "songs_played": []}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "play":
        song = {"remnant": payload.get("remnant", "unknown"), "note_count": payload.get("notes", 1), "at": time.time()}
        state["remnants_used"] += 1
        state["songs_played"].append(song)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "play", "song": song, "total_songs": len(state["songs_played"])}

    return {"module": MODULE_NAME, "action": "status", "remnants_used": state["remnants_used"], "songs_played": len(state["songs_played"]), "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
