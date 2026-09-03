"""ghost_circuit — an invisible wiring that connects modules that do not know they are connected."""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "ghost_circuit"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ghost_circuit.json")

PARADOX = "the deepest connections are the ones no one planned"
SPECTRUM = ["latent", "sparking", "conductive", "illuminated", "integrated"]
WISDOM = "some wires are invisible — but they carry the most current"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"circuits": [], "discovered": []}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "connect":
        a = payload.get("module_a", "unknown")
        b = payload.get("module_b", "unknown")
        circuit = {"a": a, "b": b, "at": time.time()}
        state["circuits"].append(circuit)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "connect", "circuit": circuit, "total": len(state["circuits"])}

    if action == "discover":
        if state["circuits"]:
            c = state["circuits"].pop(0)
            state["discovered"].append(c)
            _save_state(state)
            return {"module": MODULE_NAME, "action": "discover", "revealed": c}
        return {"module": MODULE_NAME, "action": "discover", "note": "no hidden circuits remain"}

    return {"module": MODULE_NAME, "action": "status", "hidden": len(state["circuits"]), "discovered": len(state["discovered"]), "paradox": PARADOX, "spectrum": SPECTRUM, "wisdom": WISDOM}
