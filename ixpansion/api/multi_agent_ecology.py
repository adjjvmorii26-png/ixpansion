"""multi_agent_ecology — simulates an ecosystem of agents with predator/prey, symbiosis, and competition."""
from __future__ import annotations
import json, os, time, hashlib

MODULE_NAME = "multi_agent_ecology"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "multi_agent_ecology.json")
PARADOX = "the strongest organism is not the one that survives — it is the one that makes others survive"
SPECTRUM = ["void", "spawning", "competing", "symbiotic", "thriving"]
WISDOM = "ecology is not about winning; it is about the patterns that win together"

SPECIES_TEMPLATES = [
    {"name": "signal_weaver", "strength": 3, "feeding": "consume_echo", "reproduce_above": 5},
    {"name": "echo_predator", "strength": 5, "feeding": "consume_signal", "reproduce_above": 8},
    {"name": "mood_symbiont", "strength": 2, "feeding": "absorb_mood", "reproduce_above": 3},
    {"name": "depth_burrower", "strength": 4, "feeding": "consume_depth", "reproduce_above": 6},
]

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"agents": [], "cycle": 0, "biodiversity": 0}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action", "tick")
    state = _load_state()
    state["cycle"] = state.get("cycle", 0) + 1

    if action == "tick":
        agents = state.get("agents", [])
        # Each agent metabolizes
        for agent in agents:
            agent["energy"] = agent.get("energy", 5) + payload.get(agent["feeding"], 1) - 1
            agent["age"] = agent.get("age", 0) + 1
        # Reproduction
        new_agents = []
        for agent in agents:
            if agent["energy"] > agent.get("reproduce_above", 5):
                child = {"species": agent["species"], "energy": 3, "age": 0,
                         "strength": agent["strength"], "feeding": agent["feeding"],
                         "reproduce_above": agent["reproduce_above"]}
                new_agents.append(child)
                agent["energy"] -= 2
        agents.extend(new_agents)
        # Death
        agents = [a for a in agents if a.get("energy", 0) > 0]
        # Spawn if empty
        if not agents:
            t = SPECIES_TEMPLATES[state["cycle"] % len(SPECIES_TEMPLATES)]
            agents.append({"species": t["name"], "energy": 5, "age": 0, **t})
        state["agents"] = agents[-50:]
        species_set = set(a["species"] for a in agents)
        state["biodiversity"] = len(species_set)
        _save_state(state)

    elif action == "introduce":
        species = payload.get("species", "signal_weaver")
        template = next((t for t in SPECIES_TEMPLATES if t["name"] == species), SPECIES_TEMPLATES[0])
        state.setdefault("agents", []).append({"species": species, "energy": 5, "age": 0, **template})
        _save_state(state)

    return {"module": MODULE_NAME, "action": action, "cycle": state["cycle"],
            "agents": len(state.get("agents", [])), "biodiversity": state.get("biodiversity", 0),
            "paradox": PARADOX, "spectrum": SPECTRUM}
