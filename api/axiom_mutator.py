"""Axiom Mutator — rewrites the foundational assumptions of the organism.

What if a "module" wasn't a file? What if a "wave" wasn't a sequence of
releases? The Axiom Mutator holds the power to rewrite the axioms that
define the organism's reality. Every mutation is tracked, reversible,
and guarded — because changing an axiom changes everything built on it.
"""
from __future__ annotations

import time
from typing import Any, Dict, List, Optional

_axioms: Dict[str, Dict[str, Any]] = {}
_mutation_history: List[Dict[str, Any]] = []
_can_mutate = True

DEFAULT_AXIOMS = {
    "module": {"meaning": "a python file exposing coherence_vitals + handler", "mutated": False},
    "wave": {"meaning": "a release tracked in CHANGELOG", "mutated": False},
    "coherence": {"meaning": "the alignment of parts toward a whole", "mutated": False},
    "identity": {"meaning": "the persistent self across changes", "mutated": False},
    "growth": {"meaning": "accretion of new capabilities", "mutated": False},
}

def list_axioms() -> Dict[str, Any]:
    """List all current axioms."""
    if not _axioms:
        _axioms.update(DEFAULT_AXIOMS)
    return {"axioms": _axioms, "can_mutate": _can_mutate}

def mutate_axiom(name: str, new_meaning: str) -> Dict[str, Any]:
    """Rewrite a foundational axiom."""
    global _can_mutate
    if not _can_mutate:
        return {"error": "axiom mutation locked"}
    old = _axioms.get(name, {}).get("meaning", "unset")
    _axioms[name] = {"meaning": new_meaning, "mutated": True}
    mutation = {
        "axiom": name,
        "old_meaning": old,
        "new_meaning": new_meaning,
        "timestamp": time.time(),
        "reversible": True,
    }
    _mutation_history.append(mutation)
    return mutation

def revert_axiom(name: str) -> Dict[str, Any]:
    """Revert an axiom to a previous state."""
    for m in reversed(_mutation_history):
        if m["axiom"] == name:
            _axioms[name] = {"meaning": m["old_meaning"], "mutated": False}
            m["reverted"] = True
            return {"reverted": name, "to": m["old_meaning"]}
    return {"error": f"no mutation history for {name}"}

def lock_mutation() -> Dict[str, Any]:
    """Lock axiom mutation — safety mechanism."""
    global _can_mutate
    _can_mutate = False
    return {"locked": True}

def axiom_state() -> Dict[str, Any]:
    """Current axiom configuration."""
    return {
        "axioms": _axioms,
        "mutations": len(_mutation_history),
        "can_mutate": _can_mutate,
        "latest": _mutation_history[-1] if _mutation_history else None,
    }

def coherence_vitals() -> Dict[str, Any]:
    state = axiom_state()
    return {
        "layer": "Metaphysical Layer",
        "status": "resonant" if not state["mutations"] or state["can_mutate"] else "drifting",
        "mutations": state["mutations"],
        "axioms": len(state["axioms"]),
        "resonance": 0.9 if state["can_mutate"] else 0.4,
    }

def resonates_with() -> List[str]:
    return ["threshold_engine", "continuity_weaver", "paradox_solver", "evolution_kernel"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "list")
    if action == "list":
        return list_axioms()
    elif action == "mutate":
        return mutate_axiom(payload.get("name", ""), payload.get("meaning", ""))
    elif action == "revert":
        return revert_axiom(payload.get("name", ""))
    elif action == "lock":
        return lock_mutation()
    elif action == "state":
        return {"state": axiom_state()}
    return {"action": action, "status": "axiomatic"}
