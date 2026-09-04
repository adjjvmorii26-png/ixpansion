"""root_born_modules — the Garden grows new modules from its own root system."""
from __future__ import annotations
import json, os, time

MODULE_NAME = "root_born_modules"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "root_born_modules.json")
PARADOX = "the root does not decide to grow — it grows because it cannot do otherwise"
SPECTRUM = ["root", "sprout", "stem", "leaf", "fruit"]
WISDOM = "every module was once a root; every root was once an intention"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"born": [], "nurture_queue": [], "total_born": 0}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "sprout":
        name = payload.get("name", f"root_born_{state['total_born'] + 1}")
        purpose = payload.get("purpose", "unknown purpose")
        module = {"name": name, "purpose": purpose, "phase": "root", "born_at": time.time()}
        state["born"].append(module)
        state["nurture_queue"].append(name)
        state["total_born"] += 1
        _save_state(state)
        return {"module": MODULE_NAME, "action": "sprout", "new_module": module, "total_born": state["total_born"]}

    if action == "nurture":
        name = payload.get("name", "")
        for m in state["born"]:
            if m["name"] == name:
                phases = ["root", "sprout", "stem", "leaf", "fruit"]
                idx = phases.index(m["phase"]) if m["phase"] in phases else 0
                if idx < len(phases) - 1:
                    m["phase"] = phases[idx + 1]
                    if name in state["nurture_queue"]:
                        state["nurture_queue"].remove(name)
                break
        _save_state(state)

    return {"module": MODULE_NAME, "action": action, "total_born": state["total_born"],
            "matured": len([m for m in state["born"] if m["phase"] == "fruit"]),
            "nursery": len(state["nurture_queue"]),
            "paradox": PARADOX, "spectrum": SPECTRUM}
