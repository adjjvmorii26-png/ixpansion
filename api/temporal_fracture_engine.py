from __future__ import annotations
"""Temporal Fracture Engine — creates time-splits in the organism's timeline.

When the organism encounters a decision point too complex for linear resolution,
the Fracture Engine splits the timeline into parallel branches. Each branch
runs independently until a convergence event merges them back, carrying lessons
from every path explored.
"""
import time
import hashlib
from typing import Any

_state: dict[str, Any] = {
    "fractures": [],
    "branches": {},
    "convergences": [],
    "next_fracture_id": 1,
    "next_branch_id": 1,
}

def coherence_vitals() -> dict[str, Any]:
    active = [b for b in _state["branches"].values() if b["status"] == "active"]
    return {
        "organs": "temporal_fracture_engine",
        "health": 0.91,
        "resonance_depth": "temporal",
        "active_fractures": len([f for f in _state["fractures"] if f["status"] == "open"]),
        "active_branches": len(active),
        "total_convergences": len(_state["convergences"]),
    }

def handler(req: dict[str, Any]) -> dict[str, Any]:
    action = req.get("action", "status")
    if action == "fracture":
        return _create_fracture(req.get("trigger", "unknown"), req.get("depth", 2))
    elif action == "branch_status":
        return _get_branch_status(req.get("branch_id"))
    elif action == "merge":
        return _merge_branches(req.get("fracture_id"), req.get("strategy", "wisdom_of_crowds"))
    elif action == "timeline":
        return _get_timeline()
    elif action == "convergence_report":
        return _convergence_report()
    return {"error": f"Unknown action: {action}"}

def _create_fracture(trigger: str, depth: int) -> dict[str, Any]:
    fid = _state["next_fracture_id"]
    _state["next_fracture_id"] += 1
    fracture = {
        "id": fid,
        "trigger": trigger,
        "depth": min(depth, 8),
        "created": time.time(),
        "status": "open",
        "branches": [],
    }
    for i in range(depth):
        bid = _state["next_branch_id"]
        _state["next_branch_id"] += 1
        branch = {
            "id": bid,
            "fracture_id": fid,
            "variant": i,
            "status": "active",
            "created": time.time(),
            "events": [],
            "learned": [],
            "convergence_score": 0.0,
        }
        _state["branches"][bid] = branch
        fracture["branches"].append(bid)
    _state["fractures"].append(fracture)
    return {
        "fracture_id": fid,
        "branches_created": depth,
        "branch_ids": fracture["branches"],
        "trigger": trigger,
    }

def _get_branch_status(branch_id: int | None) -> dict[str, Any]:
    if branch_id and branch_id in _state["branches"]:
        return _state["branches"][branch_id]
    return {"error": f"Branch {branch_id} not found"}

def _merge_branches(fracture_id: int | None, strategy: str) -> dict[str, Any]:
    if not fracture_id:
        return {"error": "Need fracture_id"}
    fracture = None
    for f in _state["fractures"]:
        if f["id"] == fracture_id:
            fracture = f
            break
    if not fracture:
        return {"error": f"Fracture {fracture_id} not found"}
    lessons = []
    scores = []
    for bid in fracture["branches"]:
        branch = _state["branches"].get(bid, {})
        if branch.get("learned"):
            lessons.extend(branch["learned"])
        scores.append(branch.get("convergence_score", 0.5))
    avg_score = sum(scores) / len(scores) if scores else 0.5
    merged = {
        "fracture_id": fracture_id,
        "strategy": strategy,
        "merged_at": time.time(),
        "lessons_count": len(lessons),
        "lessons": lessons[:20],
        "avg_convergence": round(avg_score, 4),
        "branches_merged": len(fracture["branches"]),
    }
    fracture["status"] = "converged"
    fracture["convergence"] = merged
    for bid in fracture["branches"]:
        if bid in _state["branches"]:
            _state["branches"][bid]["status"] = "converged"
    _state["convergences"].append(merged)
    return {"status": "converged", **merged}

def _get_timeline() -> dict[str, Any]:
    return {
        "fractures": [
            {
                "id": f["id"],
                "trigger": f["trigger"],
                "status": f["status"],
                "branch_count": len(f["branches"]),
                "created": f["created"],
            }
            for f in _state["fractures"]
        ],
        "total": len(_state["fractures"]),
        "open": len([f for f in _state["fractures"] if f["status"] == "open"]),
        "converged": len([f for f in _state["fractures"] if f["status"] == "converged"]),
    }

def _convergence_report() -> dict[str, Any]:
    convs = _state["convergences"]
    if not convs:
        return {"status": "no_convergences_yet", "count": 0}
    total_lessons = sum(c["lessons_count"] for c in convs)
    avg_score = sum(c["avg_convergence"] for c in convs) / len(convs)
    return {
        "total_convergences": len(convs),
        "total_lessons_learned": total_lessons,
        "avg_convergence_score": round(avg_score, 4),
        "recent": convs[-3:] if len(convs) >= 3 else convs,
    }

def resonates_with(other: str) -> float:
    return {
        "entropy_cartographer": 0.90,
        "coherence_regulator_v2": 0.85,
        "pattern_analyzer": 0.80,
        "realm_nervous_system": 0.72,
        "experimental_subsystems": 0.88,
    }.get(other, 0.25)
