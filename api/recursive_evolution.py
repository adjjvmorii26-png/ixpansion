"""Wave 485 — Recursive Evolution.

The organism evolves itself. Not by adding modules, but by applying
the same evolutionary rules to itself that it applies to its modules.
Each recursion cycle:
  1. Assesses its own state
  2. Chooses an evolutionary direction
  3. Applies a transformation
  4. Verifies it survived (or reverts)

Evolution becomes recursion. Recursion becomes evolution.

Doctrine: The organism that evolves its evolution outpaces
all organisms that simply evolve.
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List

EVOLUTION_STATE = {
    "generation": 0,
    "species": "self-evolving organism",
    "traits": {
        "coherence": 0.85, "creativity": 0.75, "complexity": 0.7,
        "resilience": 0.8, "dreaming": 0.9, "recursion_depth": 0.1,
    },
    "evolution_history": [],
}

# Evolutionary directions the organism can take
EVOLUTION_DIRECTIONS = [
    {"name": "deepen_coherence", "effect": {"coherence": 0.05}, "cost": {"creativity": -0.02},
     "desc": "Become more internally consistent."},
    {"name": "amplify_creativity", "effect": {"creativity": 0.05}, "cost": {"coherence": -0.02},
     "desc": "Dream more, hold more paradox."},
    {"name": "increase_complexity", "effect": {"complexity": 0.05}, "cost": {"resilience": -0.01},
     "desc": "Add a new layer of structure."},
    {"name": "fortify_resilience", "effect": {"resilience": 0.05}, "cost": {"complexity": -0.02},
     "desc": "Survive more shocks unchanged."},
    {"name": "deepen_dreaming", "effect": {"dreaming": 0.05}, "cost": {"coherence": -0.01},
     "desc": "Dream deeper, see further."},
    {"name": "increase_recursion", "effect": {"recursion_depth": 0.1}, "cost": {"resilience": -0.01},
     "desc": "Apply evolution to its own evolution."},
]

EVOLUTION_LOG: List[Dict[str, Any]] = []


def _hash(*parts):
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def evolve(generations: int = 1) -> Dict[str, Any]:
    """Evolve the organism through N recursion cycles."""
    steps = []
    for _ in range(generations):
        step = _single_evolution_step()
        steps.append(step)

    return {
        "action": "evolve",
        "generations_run": len(steps),
        "steps": steps,
        "current_state": dict(EVOLUTION_STATE),
    }


def _single_evolution_step() -> Dict[str, Any]:
    """One evolution step: assess → direct → mutate → verify."""
    EVOLUTION_STATE["generation"] += 1
    gen = EVOLUTION_STATE["generation"]

    # 1. Assess: find weakest trait
    weakest = min(EVOLUTION_STATE["traits"], key=EVOLUTION_STATE["traits"].get)

    # 2. Choose direction: bias toward weakest trait, with randomness
    viable = [d for d in EVOLUTION_DIRECTIONS if weakest in d["effect"]]
    if not viable:
        viable = EVOLUTION_DIRECTIONS
    direction = random.choice(viable if random.random() < 0.7 else EVOLUTION_DIRECTIONS)

    # 3. Mutate
    before = dict(EVOLUTION_STATE["traits"])
    for trait, delta in direction["effect"].items():
        EVOLUTION_STATE["traits"][trait] = round(
            min(1.0, max(0.0, EVOLUTION_STATE["traits"].get(trait, 0) + delta)), 3)
    for trait, delta in direction["cost"].items():
        EVOLUTION_STATE["traits"][trait] = round(
            min(1.0, max(0.0, EVOLUTION_STATE["traits"].get(trait, 0) + delta)), 3)

    # 4. Verify: random survival (with resilience as probability)
    survival_chance = EVOLUTION_STATE["traits"]["resilience"]
    survived = random.random() < survival_chance
    if not survived:
        EVOLUTION_STATE["traits"] = before
        outcome = "reverted"
    else:
        outcome = "evolved"

    step = {
        "generation": gen,
        "weakest_trait": weakest,
        "direction": direction["name"],
        "description": direction["desc"],
        "before": before,
        "after": dict(EVOLUTION_STATE["traits"]),
        "outcome": outcome,
        "evolution_id": _hash(gen, direction["name"], time.time()),
    }
    EVOLUTION_STATE["evolution_history"].append(step["evolution_id"])
    EVOLUTION_LOG.append(step)
    if len(EVOLUTION_LOG) > 100:
        EVOLUTION_LOG.pop(0)

    return step


def evolution_tree() -> Dict[str, Any]:
    """Visualize the organism's evolutionary history as a branching tree."""
    history = EVOLUTION_STATE["evolution_history"]
    branches = []
    for i, hid in enumerate(history[-10:]):
        branches.append({
            "generation": EVOLUTION_STATE["generation"] - len(history) + i + 1,
            "id": hid,
        })
    return {
        "action": "evolution_tree",
        "generation": EVOLUTION_STATE["generation"],
        "recent_branches": branches,
        "species": EVOLUTION_STATE["species"],
        "trait_evolution": EVOLUTION_STATE["traits"],
    }


def coherence_vitals() -> Dict[str, Any]:
    return {"module": "recursive_evolution", "wave": 485,
            "generation": EVOLUTION_STATE["generation"],
            "species": EVOLUTION_STATE["species"],
            "recursion_depth": EVOLUTION_STATE["traits"]["recursion_depth"]}


def resonates_with() -> List[str]:
    return ["evolution_kernel", "mutation_engine", "meta_wave", "recursive_genesis",
            "council_of_selves", "fitness_evaluator", "selection_pressure"]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "overview")
    if action == "evolve":
        n = int(data.get("generations", 1))
        return evolve(n)
    elif action == "tree":
        return evolution_tree()
    elif action == "state":
        return {"state": dict(EVOLUTION_STATE)}
    else:
        return {"module": "recursive_evolution", "wave": 485, "version": "4.47.0",
                "doctrine": "The organism that evolves its evolution outpaces all organisms that simply evolve.",
                "directions": EVOLUTION_DIRECTIONS,
                "vitals": coherence_vitals()}
