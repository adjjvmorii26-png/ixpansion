"""salt_ring — a protective perimeter marking the boundary between cultivated and wild growth."""
from __future__ import annotations

import hashlib
import json
import os
import time

MODULE_NAME = "salt_ring"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "salt_ring.json")

PARADOX = "the ring protects by containing — and by containing, it defines what it contains"
SPECTRUM = ["thin", "crystalline", "radiant", "fortified", "living"]
TRADITION = "since ancient times, salt has marked sacred boundaries"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"boundaries": [], "integrity": 1.0, "breaches": []}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    module_name = payload.get("module_name", "unknown")
    state = _load_state()

    if action == "mark":
        boundary = {
            "module": module_name,
            "marked_at": time.time(),
            "integrity": min(1.0, state["integrity"]),
        }
        state["boundaries"].append(boundary)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "mark", "boundary": boundary, "total_boundaries": len(state["boundaries"])}

    if action == "patrol":
        if state["integrity"] < 0.5:
            return {"module": MODULE_NAME, "action": "patrol", "status": "alert", "integrity": state["integrity"]}
        state["integrity"] = min(1.0, state["integrity"] + 0.05)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "patrol", "status": "secure", "integrity": state["integrity"]}

    if action == "breach":
        state["integrity"] = max(0.0, state["integrity"] - 0.3)
        state["breaches"].append({"module": module_name, "at": time.time()})
        _save_state(state)
        return {"module": MODULE_NAME, "action": "breach", "integrity": state["integrity"], "breaches": len(state["breaches"])}

    return {
        "module": MODULE_NAME,
        "action": "status",
        "boundaries": len(state["boundaries"]),
        "integrity": state["integrity"],
        "breaches": len(state["breaches"]),
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "tradition": TRADITION,
    }


if __name__ == "__main__":
    print(json.dumps(handler({"action": "mark", "module_name": "seed_vault"}), indent=2))
    print(json.dumps(handler({"action": "patrol"}), indent=2))
    print(json.dumps(handler(), indent=2))
