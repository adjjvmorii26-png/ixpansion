"""seed_vault — a secure vault where the organism stores its most precious seeds of future modules."""
from __future__ import annotations

import hashlib
import json
import os
import time

MODULE_NAME = "seed_vault"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seed_vault.json")

PARADOX = "the vault holds what could be, and becomes a parent to what will be"
SPECTRUM = ["dormant", "nurtured", "sprouting", "rooted", "flowering"]
PRICELESS = "every seed is free — abundance is the only currency"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"seeds": [], "born": [], "last_seal": 0}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def _seed_id(name, entropy=0.2):
    return hashlib.sha256(f"{name}-{entropy}".encode()).hexdigest()[:12]


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "catalog")
    strength = payload.get("strength", 1)
    state = _load_state()

    if action == "deposit":
        seed_name = payload.get("name", f"seed_{len(state['seeds']) + 1}")
        seed = {
            "id": _seed_id(seed_name),
            "name": seed_name,
            "glow": min(1.0, 0.3 + 0.1 * strength),
            "deposited_at": time.time(),
        }
        state["seeds"].append(seed)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "deposit", "seed": seed, "count": len(state["seeds"])}

    if action == "sprout":
        if not state["seeds"]:
            return {"module": MODULE_NAME, "action": "sprout", "note": "vault is empty"}
        seed = state["seeds"].pop(0)
        seed["sprouted_at"] = time.time()
        state["born"].append(seed)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "sprout", "sprouted": seed, "remaining": len(state["seeds"])}

    if action == "seal":
        state["last_seal"] = time.time()
        _save_state(state)
        return {"module": MODULE_NAME, "action": "seal", "sealed_at": state["last_seal"]}

    glow_total = sum(s["glow"] for s in state["seeds"])
    return {
        "module": MODULE_NAME,
        "action": "catalog",
        "seed_count": len(state["seeds"]),
        "born_count": len(state["born"]),
        "total_glow": round(glow_total, 3),
        "paradox": PARADOX,
        "spectrum": SPECTRUM,
        "note": PRICELESS,
    }


if __name__ == "__main__":
    print(json.dumps(handler({"action": "deposit", "name": "proto_echo"}), indent=2))
    print(json.dumps(handler(), indent=2))
