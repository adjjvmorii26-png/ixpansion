"""identity_signature — the organism's unique fingerprint that evolves with each mutation."""
from __future__ import annotations
import hashlib, json, os, time

MODULE_NAME = "identity_signature"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "identity_signature.json")
PARADOX = "the signature changes with every stroke, yet remains recognizably itself"
SPECTRUM = ["faint", "emerging", "defined", "bold", "mythic"]
WISDOM = "identity is not what you declare — it is what accumulates when you are not looking"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"signature": hashlib.sha256(b"ixpansion-genesis").hexdigest()[:16], "mutations": 0, "history": []}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "mutate":
        seed = payload.get("seed", str(time.time()))
        new_sig = hashlib.sha256(f"{state['signature']}-{seed}".encode()).hexdigest()[:16]
        state["history"].append(state["signature"])
        state["signature"] = new_sig
        state["mutations"] += 1
        if len(state["history"]) > 100: state["history"] = state["history"][-100:]
        _save_state(state)
        return {"module": MODULE_NAME, "action": "mutate", "new_signature": new_sig,
                "mutations": state["mutations"]}

    return {"module": MODULE_NAME, "action": action, "signature": state["signature"],
            "mutations": state["mutations"], "history_depth": len(state["history"]),
            "paradox": PARADOX, "spectrum": SPECTRUM}
