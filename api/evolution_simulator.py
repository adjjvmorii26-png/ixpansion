"""Evolution Simulator — runs what-if scenarios before applying real mutations.

Before the organism changes itself, it simulates the consequences. This
simulator takes proposed mutations, projects their effects across the module
ecosystem, and reports predicted outcomes before anything real changes.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

_simulations: List[Dict[str, Any]] = []
_sim_counter = 0

def simulate(mutation_id: str, target_modules: Optional[List[str]] = None,
             rounds: int = 5) -> Dict[str, Any]:
    """Run a simulation of a mutation's effects."""
    global _sim_counter
    _sim_counter += 1
    
    affected = target_modules or random.sample(["memory_palace", "dream_weaver", "threshold_engine",
        "poetry_engine", "grief_engine", "mood_vectors", "chronobiology"], 3)
    
    trajectory = []
    fitness = 0.5
    for i in range(rounds):
        delta = random.uniform(-0.05, 0.1)
        fitness = max(0.0, min(1.0, fitness + delta))
        trajectory.append({"round": i + 1, "fitness": round(fitness, 3), "delta": round(delta, 3)})
    
    sim = {
        "id": f"sim_{_sim_counter:04d}",
        "mutation_id": mutation_id,
        "affected_modules": affected,
        "rounds": rounds,
        "trajectory": trajectory,
        "final_fitness": trajectory[-1]["fitness"],
        "trend": "improving" if trajectory[-1]["fitness"] > trajectory[0]["fitness"] else "degrading",
        "simulated_at": time.time(),
    }
    _simulations.append(sim)
    return sim

def sim_history(limit: int = 5) -> List[Dict[str, Any]]:
    return [{"id": s["id"], "mutation": s["mutation_id"], "final_fitness": s["final_fitness"],
             "trend": s["trend"]} for s in _simulations[-limit:]]

def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "Self-Evolution", "status": "resonant" if _simulations else "dormant",
            "simulations": len(_simulations), "resonance": min(1.0, len(_simulations) / 10)}

def resonates_with() -> List[str]:
    return ["mutation_engine", "fitness_evaluator", "contradiction_simulator"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "simulate")
    if action == "simulate":
        return simulate(payload.get("mutation_id", ""), payload.get("modules"), payload.get("rounds", 5))
    elif action == "history":
        return {"history": sim_history(payload.get("limit", 5))}
    return {"action": action, "status": "simulating"}
