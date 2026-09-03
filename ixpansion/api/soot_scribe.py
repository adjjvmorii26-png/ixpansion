"""soot_scribe — writes with ash from the kiln — records the fire's own memory."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "soot_scribe"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "soot_scribe.json")

PARADOX = "the fire writes its own story in soot — the scribe merely reads it"
SPECTRUM = ["smoke", "ash", "imprint", "glyph", "codex"]
WISDOM = "every fire leaves a manuscript behind"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"inscriptions": [], "last_written": None}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "write":
        inscription = {"content": payload.get("content", ""), "glyph": payload.get("glyph", "?"), "at": time.time()}
        state["inscriptions"].append(inscription)
        state["last_written"] = inscription
        _save_state(state)
        return {"module": MODULE_NAME, "action": "write", "inscription": inscription, "total": len(state["inscriptions"])}

    return {"module": MODULE_NAME, "action": "status", "inscriptions": len(state["inscriptions"]), "last_written": state["last_written"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
