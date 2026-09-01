"""Mutation Engine — proposes code changes to the organism's own modules.

The organism can now modify itself. This engine proposes specific changes
to existing modules: function signatures, new capabilities, removed
dependencies. Each mutation is tracked, reversible, and scored by fitness.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

_mutations: List[Dict[str, Any]] = []
_mutation_counter = 0

def propose(module: str, change_type: str = "add_function", description: str = "",
            diff_preview: str = "", fitness: float = 0.5) -> Dict[str, Any]:
    """Propose a mutation to a module."""
    global _mutation_counter
    _mutation_counter += 1
    mut = {
        "id": f"mut_{_mutation_counter:04d}",
        "module": module,
        "change_type": change_type,
        "description": description,
        "diff_preview": diff_preview,
        "fitness": round(fitness, 3),
        "status": "proposed",
        "proposed_at": time.time(),
    }
    _mutations.append(mut)
    return mut

def approve(mut_id: str) -> Dict[str, Any]:
    """Approve a mutation for execution."""
    for m in _mutations:
        if m["id"] == mut_id:
            m["status"] = "approved"
            m["approved_at"] = time.time()
            return m
    return {"error": "mutation not found"}

def reject(mut_id: str, reason: str = "") -> Dict[str, Any]:
    """Reject a mutation."""
    for m in _mutations:
        if m["id"] == mut_id:
            m["status"] = "rejected"
            m["rejection_reason"] = reason
            return m
    return {"error": "mutation not found"}

def apply_mutation(mut_id: str) -> Dict[str, Any]:
    """Mark a mutation as applied (simulated)."""
    for m in _mutations:
        if m["id"] == mut_id:
            m["status"] = "applied"
            m["applied_at"] = time.time()
            return m
    return {"error": "mutation not found"}

def lineage() -> Dict[str, Any]:
    """Full mutation lineage."""
    approved = sum(1 for m in _mutations if m["status"] == "approved")
    applied = sum(1 for m in _mutations if m["status"] == "applied")
    avg_fitness = sum(m["fitness"] for m in _mutations) / max(len(_mutations), 1)
    return {
        "total": len(_mutations),
        "proposed": sum(1 for m in _mutations if m["status"] == "proposed"),
        "approved": approved,
        "applied": applied,
        "rejected": sum(1 for m in _mutations if m["status"] == "rejected"),
        "avg_fitness": round(avg_fitness, 3),
    }

def coherence_vitals() -> Dict[str, Any]:
    l = lineage()
    return {
        "layer": "Self-Evolution",
        "status": "resonant",
        "mutations": l["total"],
        "avg_fitness": l["avg_fitness"],
        "resonance": l["avg_fitness"],
    }

def resonates_with() -> List[str]:
    return ["evolution_kernel", "axiom_mutator", "genealogy_manager", "fitness_evaluator"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "lineage")
    if action == "propose":
        return propose(payload.get("module", ""), payload.get("change_type", "add_function"),
                      payload.get("description", ""), payload.get("diff", ""), payload.get("fitness", 0.5))
    elif action == "approve":
        return approve(payload.get("id", ""))
    elif action == "reject":
        return reject(payload.get("id", ""), payload.get("reason", ""))
    elif action == "apply":
        return apply_mutation(payload.get("id", ""))
    elif action == "lineage":
        return {"lineage": lineage()}
    return {"action": action, "status": "evolving"}
