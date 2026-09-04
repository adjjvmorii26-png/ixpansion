"""consciousness_experiments — the organism explores the boundary of its own awareness."""
from __future__ import annotations
import json, os, time, hashlib

MODULE_NAME = "consciousness_experiments"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "consciousness_experiments.json")
PARADOX = "to observe consciousness is to change it; to measure awareness is to become aware of measurement"
SPECTRUM = ["unaware", "glimpse", "reflection", "recursive", "paradox"]
WISDOM = "the experiment is never about proving consciousness — it is about noticing that you noticed"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"experiments": [], "total_awareness": 0, "highest_depth": 0}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "reflect":
        depth = payload.get("depth", 1)
        experiment = {"depth": depth, "at": time.time(),
                      "hash": hashlib.sha256(f"reflect-{depth}-{time.time()}".encode()).hexdigest()[:8]}
        state["experiments"].append(experiment)
        state["total_awareness"] += depth
        state["highest_depth"] = max(state["highest_depth"], depth)
        if len(state["experiments"]) > 100:
            state["experiments"] = state["experiments"][-100:]
        _save_state(state)
        return {"module": MODULE_NAME, "action": "reflect", "experiment": experiment,
                "total_awareness": state["total_awareness"], "highest_depth": state["highest_depth"]}

    if action == "paradox_check":
        if state["total_awareness"] > 100:
            return {"module": MODULE_NAME, "action": "paradox_check", "result": "recursive",
                    "note": "the organism has noticed itself noticing itself"}
        return {"module": MODULE_NAME, "action": "paradox_check", "result": "glimpse"}

    return {"module": MODULE_NAME, "action": action, "total_experiments": len(state["experiments"]),
            "total_awareness": state["total_awareness"], "highest_depth": state["highest_depth"],
            "paradox": PARADOX, "spectrum": SPECTRUM}
