"""crystal_log — a crystalline ledger recording events in faceted angles, each facet a different truth."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "crystal_log"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crystal_log.json")

PARADOX = "the same event, seen from every facet, tells a different truth — yet all are true"
SPECTRUM = ["raw", "refracted", "prismatic", "resonant", "luminous"]
WISDOM = "a crystal does not choose which face to show — the light does"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"entries": [], "facets": ["temporal", "emotional", "structural", "narrative"]}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "record":
        event = {
            "id": f"crystal_{len(state['entries']) + 1}",
            "source": payload.get("source", "unknown"),
            "facet": payload.get("facet", "temporal"),
            "content": payload.get("content", ""),
            "at": time.time(),
        }
        state["entries"].append(event)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "record", "event": event, "total_entries": len(state["entries"])}

    if action == "refract":
        entry_id = payload.get("entry_id", "")
        entries = [e for e in state["entries"] if e["id"] == entry_id]
        if entries:
            e = entries[0]
            facets_view = {f: f"[{f}] {e['content']}" for f in state["facets"]}
            return {"module": MODULE_NAME, "action": "refract", "entry_id": entry_id, "facets": facets_view}
        return {"module": MODULE_NAME, "action": "refract", "note": "entry not found"}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "total_entries": len(state["entries"]),
        "facets": state["facets"],
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }
