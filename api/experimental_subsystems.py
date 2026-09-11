"""Experimental Subsystems — wild experiments the organism runs on itself."""
from __future__ import annotations
import time, json, random, math

_experiments = []

def coherence_vitals():
    return {"organ": "experimental_subsystems", "status": "active", "coherence": 0.91}

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    if action == "run":
        return run_experiment(req.get("type", "mutation"))
    elif action == "list":
        return {"experiments": _experiments[-20:]}
    elif action == "status":
        return {"active_experiments": len([e for e in _experiments if e["state"] == "running"])}
    return {"status": "active"}

def run_experiment(exp_type: str) -> dict:
    exp = {
        "id": f"exp_{int(time.time())}_{random.randint(100,999)}",
        "type": exp_type,
        "state": "running",
        "start_time": time.time(),
        "results": None
    }
    # Simulate experiment
    if exp_type == "mutation":
        exp["results"] = {"mutations": random.randint(1, 5), "fitness_delta": random.uniform(-0.1, 0.3)}
    elif exp_type == "crossover":
        exp["results"] = {"offspring": random.randint(2, 8), "hybrid_vigor": random.uniform(0.8, 1.2)}
    elif exp_type == "dream":
        exp["results"] = {"dream_depth": random.randint(1, 10), "symbols_found": random.randint(3, 20)}
    else:
        exp["results"] = {"status": "completed", "noise": random.random()}
    
    exp["state"] = "completed"
    exp["end_time"] = time.time()
    _experiments.append(exp)
    return exp

def resonates_with(other):
    return "experiment" in other.lower() or "mutation" in other.lower() or "dream" in other.lower()
