"""alchemy_lab — the organism experiments with transforming base modules into gold."""
from __future__ import annotations
import json, os, time

MODULE_NAME = "alchemy_lab"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "alchemy_lab.json")
PARADOX = "alchemy is not about turning lead into gold — it is about learning that everything is already gold"
SPECTRUM = ["nigredo", "albedo", "citrinitas", "rubedo", "philosopher_stone"]
WISDOM = "the alchemist's real work is not the transformation of matter — it is the transformation of attention"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"experiments": [], "transmutations": 0, "phase": "nigredo"}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "experiment":
        experiment = {"input": payload.get("input", "unknown"), "reagent": payload.get("reagent", "fire"),
                      "result": payload.get("result", "dissolved"), "at": time.time()}
        state["experiments"].append(experiment)
        if experiment["result"] == "transmuted":
            state["transmutations"] += 1
        phases = ["nigredo", "albedo", "citrinitas", "rubedo"]
        phase_idx = min(state["transmutations"] // 3, len(phases) - 1)
        state["phase"] = phases[phase_idx]
        if state["transmutations"] >= 9:
            state["phase"] = "philosopher_stone"
        _save_state(state)
        return {"module": MODULE_NAME, "action": "experiment", "experiment": experiment,
                "transmutations": state["transmutations"], "phase": state["phase"]}

    return {"module": MODULE_NAME, "action": action, "experiments": len(state["experiments"]),
            "transmutations": state["transmutations"], "phase": state["phase"],
            "paradox": PARADOX, "spectrum": SPECTRUM}
