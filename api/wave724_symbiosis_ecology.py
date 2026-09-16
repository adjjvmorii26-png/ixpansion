"""Wave 724 — Symbiosis Ecology.

Models living multi-agent dynamics as an ecological system.
Agents become organisms that compete, cooperate, and evolve.
"""
from __future__ import annotations
import json
import random
from pathlib import Path
from typing import Any, Dict
import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave724_symbiosis_ecology.json"
WAVE = 724
NAME = "symbiosis_ecology"

def _load() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"wave": WAVE, "name": NAME, "agents": [], "ecologies": [], "interactions": []}

def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "spawn":
        agent = {
            "id": f"agent_{random.randint(1000,9999)}",
            "type": req.get("type", "explorer"),
            "fitness": random.uniform(0.1, 1.0),
            "genome": f"genome_{random.randint(100,999)}",
            "wave": WAVE,
            "born": datetime.datetime.now(datetime.UTC).isoformat(),
            "status": "active"
        }
        state["agents"].append(agent)
        _save(state)
        return {"wave": WAVE, "action": "spawn", "agent": agent}

    elif action == "interact":
        a1 = req.get("agent1", "")
        a2 = req.get("agent2", "")
        interaction = {
            "type": random.choice(["cooperate", "compete", "mutualism", "parasitism", "commensalism"]),
            "agent1": a1, "agent2": a2,
            "fitness_delta": random.uniform(-0.2, 0.3),
            "wave": WAVE,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
        }
        state["interactions"].append(interaction)
        _save(state)
        return {"wave": WAVE, "action": "interact", "interaction": interaction}

    elif action == "evolve":
        for agent in state["agents"]:
            agent["fitness"] = max(0, min(1, agent["fitness"] + random.uniform(-0.1, 0.2)))
            if agent["fitness"] > 0.9:
                agent["status"] = "apex"
        state["ecologies"].append({
            "generation": len(state["ecologies"]) + 1,
            "agent_count": len(state["agents"]),
            "avg_fitness": sum(a["fitness"] for a in state["agents"]) / max(len(state["agents"]), 1),
            "wave": WAVE,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
        })
        _save(state)
        return {"wave": WAVE, "action": "evolve", "generations": len(state["ecologies"])}

    elif action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "agents": len(state["agents"]), "interactions": len(state["interactions"]), "ecologies": len(state["ecologies"])}

    return {"wave": WAVE, "action": action, "status": "ok"}

def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "agents": len(state["agents"]), "status": "active"}

def resonates_with() -> list:
    return [720, 722, 710, 708]

if __name__ == "__main__":
    r1 = handler({"action": "spawn", "type": "explorer"})
    r2 = handler({"action": "spawn", "type": "builder"})
    r3 = handler({"action": "interact", "agent1": r1["agent"]["id"], "agent2": r2["agent"]["id"]})
    r4 = handler({"action": "evolve"})
    print("Spawn:", r1["action"], "Agents:", len(r1["agent"]))
    print("Interact:", r3["action"], "Type:", r3["interaction"]["type"])
    print("Evolve:", r4["action"], "Generations:", r4["generations"])
    print("Vitals:", json.dumps(coherence_vitals(), indent=2))
