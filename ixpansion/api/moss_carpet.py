"""moss_carpet — a soft layer that grows over older modules, preserving them while connecting them."""
from __future__ import annotations

import hashlib
import json
import os
import time

MODULE_NAME = "moss_carpet"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "moss_carpet.json")

PARADOX = "to be covered in moss is not to be lost — it is to be held"
SPECTRUM = ["dusting", "settling", "spreading", "thriving", "grove"]
WISDOM = "old roots and new shoots share the same soil"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"covered": [], "connections": []}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    module_name = payload.get("module_name", "unknown")
    state = _load_state()

    if action == "grow":
        layer = {
            "module": module_name,
            "thickness": min(1.0, 0.2 + 0.15 * len(state["covered"])),
            "grew_at": time.time(),
        }
        state["covered"].append(layer)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "grow", "layer": layer, "covered_count": len(state["covered"])}

    if action == "connect":
        source = payload.get("source", module_name)
        target = payload.get("target", "evolution")
        conn = {"source": source, "target": target, "at": time.time()}
        state["connections"].append(conn)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "connect", "connection": conn, "connections": len(state["connections"])}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "modules_covered": len(state["covered"]),
        "growing_connections": len(state["connections"]),
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "wisdom": WISDOM,
    }


if __name__ == "__main__":
    print(json.dumps(handler({"action": "grow", "module_name": "seed_vault"}), indent=2))
