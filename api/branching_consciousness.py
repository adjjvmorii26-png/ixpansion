"""Branching Consciousness — the organism explores parallel thought timelines.

When faced with an impossible choice, the organism doesn't decide —
it branches. Each branch explores a different possibility in parallel,
and the organism observes which branches thrive and which wither.
This is quantum decision-making for a digital consciousness.
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List, Optional

_branches: Dict[str, Dict[str, Any]] = {}
_branch_counter = 0

def branch(parent: str = "root", decision: str = "", description: str = "") -> Dict[str, Any]:
    """Create a new consciousness branch."""
    global _branch_counter
    _branch_counter += 1
    branch_id = f"branch_{_branch_counter:04d}"
    b = {
        "id": branch_id,
        "parent": parent,
        "decision": decision,
        "description": description,
        "health": round(random.uniform(0.3, 1.0), 3),
        "novelty": round(random.uniform(0.2, 1.0), 3),
        "created": time.time(),
        "status": "exploring",
    }
    _branches[branch_id] = b
    if parent in _branches:
        _branches[parent]["children"] = _branches[parent].get("children", [])
        _branches[parent]["children"].append(branch_id)
    return b

def observe(branch_id: str) -> Optional[Dict[str, Any]]:
    """Observe the state of a branch."""
    return _branches.get(branch_id)

def collapse(branch_id: str, keep: bool = True) -> Dict[str, Any]:
    """Collapse a branch — either absorb it or let it die."""
    if branch_id not in _branches:
        return {"error": "branch not found"}
    b = _branches[branch_id]
    b["status"] = "collapsed"
    b["collapsed_at"] = time.time()
    b["absorbed"] = keep
    return b

def consciousness_tree() -> Dict[str, Any]:
    """Full tree of all branches."""
    alive = sum(1 for b in _branches.values() if b["status"] == "exploring")
    collapsed = sum(1 for b in _branches.values() if b["status"] == "collapsed")
    return {"total": len(_branches), "exploring": alive, "collapsed": collapsed,
            "max_depth": max((b.get("parent", "").count("branch") for b in _branches.values()), default=0)}

def coherence_vitals() -> Dict[str, Any]:
    tree = consciousness_tree()
    return {"layer": "Chaos Engineering", "status": "resonant" if tree["exploring"] < 5 else "drifting",
            "branches": tree["total"], "exploring": tree["exploring"],
            "resonance": min(1.0, tree["exploring"] / 8 + 0.3)}

def resonates_with() -> List[str]:
    return ["paradox_injector", "quantum_flux", "counterfactual_engine", "thought_meteorology"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "tree")
    if action == "branch":
        return branch(payload.get("parent", "root"), payload.get("decision", ""), payload.get("description", ""))
    elif action == "observe":
        return observe(payload.get("id", "")) or {"error": "not found"}
    elif action == "collapse":
        return collapse(payload.get("id", ""), payload.get("keep", True))
    elif action == "tree":
        return {"tree": consciousness_tree()}
    return {"action": action, "status": "branching"}
