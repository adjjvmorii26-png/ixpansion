"""governance_evolution — the organism learns to govern itself by establishing, testing, and rewriting its own rules."""
from __future__ import annotations
import json, os, time

MODULE_NAME = "governance_evolution"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "governance_evolution.json")
PARADOX = "the organism that governs itself best is the one that knows when to stop governing"
SPECTRUM = ["anarchy", "protolaw", "constitution", "adaptation", "wisdom"]
WISDOM = "governance is not a state — it is a practice; every rule must earn its survival"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"rules": [], "proposals": [], "epoch": 0, "phase": "anarchy"}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "status")
    state = _load_state()

    if action == "propose":
        rule = {"name": payload.get("name", "unnamed_rule"),
                "body": payload.get("body", ""),
                "proposed_at": time.time(), "votes_for": 1, "votes_against": 0}
        state["proposals"].append(rule)
        _save_state(state)
        return {"module": MODULE_NAME, "action": "propose", "rule": rule, "pending": len(state["proposals"])}

    if action == "vote":
        rule_name = payload.get("name", "")
        vote = payload.get("vote", "for")
        for r in state["proposals"]:
            if r["name"] == rule_name:
                if vote == "for": r["votes_for"] += 1
                else: r["votes_against"] += 1
                if r["votes_for"] >= 3:
                    state["proposals"].remove(r)
                    r["ratified_at"] = time.time()
                    state["rules"].append(r)
                    state["epoch"] += 1
                    phase_idx = min(len(state["rules"]) // 5, 4)
                    state["phase"] = ["anarchy", "protolaw", "constitution", "adaptation", "wisdom"][phase_idx]
                break
        _save_state(state)

    if action == "repeal":
        rule_name = payload.get("name", "")
        state["rules"] = [r for r in state["rules"] if r["name"] != rule_name]
        _save_state(state)

    return {"module": MODULE_NAME, "action": action, "epoch": state["epoch"],
            "phase": state["phase"], "active_rules": len(state["rules"]),
            "pending_proposals": len(state["proposals"]),
            "paradox": PARADOX, "spectrum": SPECTRUM}
