"""honeycomb_index — hexagonal filing system where every cell connects to six others."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "honeycomb_index"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "honeycomb_index.json")

PARADOX = "a cell with six neighbors is never alone and never crowded"
SPECTRUM = ["wax", "cell", "comb", "hive", "colony"]
WISDOM = "efficiency that crushes the bee is no efficiency at all"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"cells": [], "neighbors_total": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "insert":
        value = payload.get("value", "")
        cell = {"value": value, "connected_cells": payload.get("neighbors", ["elsewhere"]), "at": time.time()}
        state["cells"].append(cell)
        state["neighbors_total"] += len(cell["connected_cells"])
        _save_state(state)
        return {"module": MODULE_NAME, "action": "insert", "cell": cell, "total_cells": len(state["cells"])}

    return {"module": MODULE_NAME, "action": "status", "total_cells": len(state["cells"]), "total_neighbors": state["neighbors_total"], "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
