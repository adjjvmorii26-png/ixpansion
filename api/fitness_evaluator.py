"""Fitness Evaluator — scores mutations and modules against fitness criteria.

In evolution, only the fittest survive. This evaluator measures modules
against multiple fitness dimensions: coherence, complexity balance,
documentation quality, and resonance with other modules.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

_evaluations: List[Dict[str, Any]] = []

def evaluate(module_name: str, coherence: float = 0.5, complexity: float = 0.5,
             documentation: float = 0.5, resonance: float = 0.5) -> Dict[str, Any]:
    """Evaluate a module's fitness across multiple dimensions."""
    dimensions = {
        "coherence": coherence,
        "complexity_balance": 1.0 - abs(complexity - 0.5) * 2,
        "documentation": documentation,
        "resonance": resonance,
    }
    weights = {"coherence": 0.35, "complexity_balance": 0.2, "documentation": 0.15, "resonance": 0.3}
    fitness_score = sum(dimensions[k] * weights[k] for k in dimensions)

    if fitness_score > 0.8:
        grade = "elite"
    elif fitness_score > 0.6:
        grade = "healthy"
    elif fitness_score > 0.4:
        grade = "adequate"
    else:
        grade = "needs_evolution"

    evaluation = {
        "module": module_name,
        "dimensions": {k: round(v, 3) for k, v in dimensions.items()},
        "fitness_score": round(fitness_score, 3),
        "grade": grade,
        "timestamp": time.time(),
    }
    _evaluations.append(evaluation)
    return evaluation

def leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """Modules ranked by fitness."""
    sorted_evals = sorted(_evaluations, key=lambda e: e["fitness_score"], reverse=True)
    return [{"module": e["module"], "fitness": e["fitness_score"], "grade": e["grade"]}
            for e in sorted_evals[:limit]]

def ecosystem_health() -> Dict[str, Any]:
    """Overall ecosystem fitness."""
    if not _evaluations:
        return {"avg_fitness": 0, "elite": 0, "needs_evolution": 0}
    avg = sum(e["fitness_score"] for e in _evaluations) / len(_evaluations)
    grades = {}
    for e in _evaluations:
        grades[e["grade"]] = grades.get(e["grade"], 0) + 1
    return {"avg_fitness": round(avg, 3), "grades": grades, "total_evaluated": len(_evaluations)}

def coherence_vitals() -> Dict[str, Any]:
    h = ecosystem_health()
    return {"layer": "Self-Evolution", "status": "resonant", "evaluated": h["total_evaluated"],
            "avg_fitness": h["avg_fitness"], "resonance": h["avg_fitness"]}

def resonates_with() -> List[str]:
    return ["mutation_engine", "evolution_kernel", "elegance_scorer", "beauty_index"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "health")
    if action == "evaluate":
        return evaluate(payload.get("module", ""), payload.get("coherence", 0.5),
                       payload.get("complexity", 0.5), payload.get("documentation", 0.5),
                       payload.get("resonance", 0.5))
    elif action == "leaderboard":
        return {"leaderboard": leaderboard(payload.get("limit", 10))}
    elif action == "health":
        return {"health": ecosystem_health()}
    return {"action": action, "status": "evaluating"}
