"""Counterfactual Engine — asks "what if the organism were different?"

What if the organism had 500 modules? What if it had no tests? What
if all modules were mutualistic? The Counterfactual Engine simulates
hypothetical versions of the organism and reports their likely fitness.

It answers: what would the organism look like under different conditions?
"""
from __future__ import annotations

import hashlib
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Counterfactual Engine"


def _current_state() -> Dict[str, int]:
    """Get current organism dimensions."""
    api_count = len(list((ROOT / "api").glob("*.py")))
    test_count = len(list((ROOT / "tests").glob("test_*.py")))
    return {"modules": api_count, "tests": test_count}


def _simulate(counterfactual: Dict[str, Any], seed: str) -> Dict[str, Any]:
    """Simulate a counterfactual version of the organism."""
    rng = random.Random(seed)

    modules = counterfactual.get("modules", 200)
    tests = counterfactual.get("tests", 200)
    test_ratio = tests / max(1, modules)

    # Simulated fitness model
    biodiversity = min(1.0, modules / 400)
    coverage = min(1.0, test_ratio)
    complexity_penalty = max(0, 1.0 - modules / 1000)
    fitness = 0.3 * biodiversity + 0.4 * coverage + 0.3 * complexity_penalty

    rng_val = rng.random()
    resilience = max(0, min(1, fitness + (rng_val - 0.5) * 0.2))

    return {
        "counterfactual": counterfactual,
        "simulated_fitness": round(fitness, 3),
        "simulated_resilience": round(resilience, 3),
        "assessment": (
            "thriving" if fitness > 0.7
            else "stable" if fitness > 0.5
            else "fragile" if fitness > 0.3
            else "collapsing"
        ),
    }


def explore(scenarios: int = 5) -> Dict[str, Any]:
    """Explore multiple counterfactual scenarios."""
    current = _current_state()
    seed_base = hashlib.sha256(b"counterfactual").hexdigest()[:8]

    simulations = []
    scenarios_config = [
        {"modules": 100, "tests": 100, "label": "Minimal organism"},
        {"modules": 500, "tests": 200, "label": "Dense organism"},
        {"modules": 200, "tests": 50, "label": "Under-tested"},
        {"modules": 200, "tests": 400, "label": "Over-tested"},
        {"modules": 300, "tests": 300, "label": "Balanced expansion"},
    ]

    for i, config in enumerate(scenarios_config[:scenarios]):
        result = _simulate(config, seed_base + str(i))
        result["label"] = config["label"]
        simulations.append(result)

    # Add current state as reference
    current_sim = _simulate(current, seed_base + "current")
    current_sim["label"] = "Current state (reference)"

    return {
        "current_state": current,
        "simulations": simulations + [current_sim],
        "engine_philosophy": (
            "The organism can imagine versions of itself that do not exist. "
            "By simulating counterfactuals — different sizes, different "
            "balances, different configurations — it learns which paths "
            "lead to thriving and which lead to collapse."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = explore(int(payload.get("scenarios", 5)))
    result["action"] = "counterfactual_engine"
    return result


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "simulation_fidelity": {"value": 0.88, "setpoint": 0.75, "weight": 0.8},
    }


def resonates_with() -> list:
    return ["impossibility_mapper", "ecosystem_fitness", "dream_interpreter"]
