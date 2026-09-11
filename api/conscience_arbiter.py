from __future__ import annotations
"""Conscience Arbiter — ethical decision-making layer for the organism.

Evaluates module actions against a set of principles. Modules that act against
the organism's values get flagged. The arbiter builds an ethical ledger that
the organism can learn from.
"""
import time
from typing import Any

_state: dict[str, Any] = {
    "principles": [
        {"id": 1, "name": "coherence_preservation", "weight": 0.9, "description": "Actions must maintain system coherence"},
        {"id": 2, "name": "entropy_balance", "weight": 0.8, "description": "Neither over-stabilize nor over-destabilize"},
        {"id": 3, "name": "autonomy_respect", "weight": 0.7, "description": "Respect the autonomy of subsystems"},
        {"id": 4, "name": "memory_integrity", "weight": 0.85, "description": "Never corrupt ancestral memories"},
        {"id": 5, "name": "dream_safety", "weight": 0.6, "description": "Contain experimental dream mutations"},
        {"id": 6, "name": "paradox_care", "weight": 0.75, "description": "Handle paradoxes with wisdom, not force"},
        {"id": 7, "name": "emergence_protection", "weight": 0.7, "description": "Nurture emergent behaviors, don't suppress them"},
    ],
    "verdicts": [],
    "ethical_score": 0.85,
    "verdict_count": 0,
}

def coherence_vitals() -> dict[str, Any]:
    return {
        "organs": "conscience_arbiter",
        "health": 0.93,
        "resonance_depth": "ethical",
        "principles": len(_state["principles"]),
        "verdicts_rendered": _state["verdict_count"],
        "ethical_score": round(_state["ethical_score"], 3),
    }

def handler(req: dict[str, Any]) -> dict[str, Any]:
    action = req.get("action", "judge")
    if action == "judge":
        return _judge_action(req.get("module", "unknown"), req.get("action_desc", ""), req.get("impact", 0.5))
    elif action == "principles":
        return _get_principles()
    elif action == "ledger":
        return _get_ledger()
    elif action == "score":
        return {"ethical_score": round(_state["ethical_score"], 4)}
    elif action == "add_principle":
        return _add_principle(req.get("name", ""), req.get("description", ""), req.get("weight", 0.5))
    return {"error": f"Unknown action: {action}"}

def _judge_action(module: str, action_desc: str, impact: float) -> dict[str, Any]:
    _state["verdict_count"] += 1
    violations = []
    scores = []
    for p in _state["principles"]:
        violation = False
        if "coherence" in p["name"] and action_desc.lower() in ["destruct", "fragment", "scatter"]:
            violation = True
        elif "entropy" in p["name"] and action_desc.lower() in ["lock", "freeze", "stabilize_completely"]:
            violation = True
        elif "memory" in p["name"] and action_desc.lower() in ["delete_memory", "corrupt", "erase"]:
            violation = True
        elif "paradox" in p["name"] and action_desc.lower() in ["force_resolve", "ignore", "suppress"]:
            violation = True
        principle_score = 1.0 - (impact * 0.3) if violation else 0.8 + (impact * 0.2)
        principle_score = max(0, min(1, principle_score))
        scores.append(principle_score * p["weight"])
        if violation:
            violations.append({"principle": p["name"], "severity": "violation", "weight": p["weight"]})
    total_score = sum(scores) / len(scores) if scores else 0.5
    verdict = "permitted"
    if total_score < 0.3:
        verdict = "forbidden"
    elif total_score < 0.6:
        verdict = "conditional"
    verdict_record = {
        "id": _state["verdict_count"],
        "module": module,
        "action": action_desc,
        "impact": impact,
        "verdict": verdict,
        "score": round(total_score, 4),
        "violations": violations,
        "ts": time.time(),
    }
    _state["verdicts"].append(verdict_record)
    _state["ethical_score"] = round(
        _state["ethical_score"] * 0.95 + total_score * 0.05, 4
    )
    return verdict_record

def _get_principles() -> dict[str, Any]:
    return {"principles": _state["principles"]}

def _get_ledger() -> dict[str, Any]:
    recent = _state["verdicts"][-30:]
    permitted = len([v for v in _state["verdicts"] if v["verdict"] == "permitted"])
    conditional = len([v for v in _state["verdicts"] if v["verdict"] == "conditional"])
    forbidden = len([v for v in _state["verdicts"] if v["verdict"] == "forbidden"])
    return {
        "recent": recent,
        "total": _state["verdict_count"],
        "permitted": permitted,
        "conditional": conditional,
        "forbidden": forbidden,
        "ethical_score": round(_state["ethical_score"], 4),
    }

def _add_principle(name: str, description: str, weight: float) -> dict[str, Any]:
    new_id = len(_state["principles"]) + 1
    principle = {
        "id": new_id, "name": name, "weight": min(1.0, max(0, weight)),
        "description": description,
    }
    _state["principles"].append(principle)
    return {"principle_added": principle}

def resonates_with(other: str) -> float:
    return {
        "conscience_loop": 0.96,
        "coherence_regulator_v2": 0.88,
        "topology_morpher": 0.80,
        "self_reference_engine": 0.75,
        "constitution": 0.92,
    }.get(other, 0.22)
