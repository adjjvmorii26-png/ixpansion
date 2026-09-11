from __future__ import annotations
"""Topology Morpher — the organism reshapes its own network topology.

The organism can morph between network configurations: star, ring, mesh,
hierarchical, chaotic. Each topology optimizes different behaviors —
star = central control, mesh = resilience, ring = continuity, chaotic = exploration.
"""
import time
import math
from typing import Any

_state: dict[str, Any] = {
    "current_topology": "star",
    "node_count": 12,
    "morph_history": [],
    "topology_metrics": {},
    "last_morph": 0,
}

TOPOLOGIES_INFO = {
    "star": {
        "description": "Central hub controls all nodes. Optimal for command and oversight.",
        "strength": "single_source_of_truth",
        "weakness": "central_failure_point",
        "latency": 1.0,
        "resilience": 0.2,
        "autonomy": 0.1,
    },
    "ring": {
        "description": "Nodes form a circle; data flows in a loop. Optimal for continuity and equality.",
        "strength": "distributed_continuity",
        "weakness": "slow_propagation",
        "latency": 2.0,
        "resilience": 0.5,
        "autonomy": 0.4,
    },
    "mesh": {
        "description": "Every node connects to many others. Optimal for resilience and robustness.",
        "strength": "redundant_pathways",
        "weakness": "high_communication_overhead",
        "latency": 0.7,
        "resilience": 0.9,
        "autonomy": 0.5,
    },
    "hierarchical": {
        "description": "Levels of control from root to leaves. Optimal for structured governance.",
        "strength": "clear_governance",
        "weakness": "rigid_adaptation",
        "latency": 1.5,
        "resilience": 0.4,
        "autonomy": 0.2,
    },
    "chaotic": {
        "description": "Connections form unpredictably. Optimal for exploration and serendipity.",
        "strength": "novel_pattern_discovery",
        "weakness": "unpredictable_behavior",
        "latency": 0.9,
        "resilience": 0.6,
        "autonomy": 0.9,
    },
}

def coherence_vitals() -> dict[str, Any]:
    return {
        "organs": "topology_morpher",
        "health": 0.91,
        "resonance_depth": "architectural",
        "current_topology": _state["current_topology"],
        "morph_count": len(_state["morph_history"]),
        "nodes": _state["node_count"],
    }

def handler(req: dict[str, Any]) -> dict[str, Any]:
    action = req.get("action", "status")
    if action == "status":
        return _get_status()
    elif action == "morph":
        return _morph(req.get("target", ""), req.get("reason", "evolution"))
    elif action == "topologies":
        return _list_topologies()
    elif action == "history":
        return {"history": _state["morph_history"]}
    elif action == "metrics":
        return _get_metrics()
    return {"error": f"Unknown action: {action}"}

def _morph(target: str, reason: str) -> dict[str, Any]:
    if target not in TOPOLOGIES_INFO:
        return {"error": f"Unknown topology: {target}. Available: {list(TOPOLOGIES_INFO.keys())}"}
    prev = _state["current_topology"]
    _state["current_topology"] = target
    _state["last_morph"] = time.time()
    morph = {
        "from": prev,
        "to": target,
        "reason": reason,
        "ts": time.time(),
        "nodes_affected": _state["node_count"],
    }
    _state["morph_history"].append(morph)
    _update_metrics()
    return {"status": f"morphed_{prev}_to_{target}", **morph}

def _list_topologies() -> dict[str, Any]:
    return {
        "topologies": [
            {"name": name, **info}
            for name, info in TOPOLOGIES_INFO.items()
        ],
        "current": _state["current_topology"],
    }

def _get_status() -> dict[str, Any]:
    info = TOPOLOGIES_INFO.get(_state["current_topology"], {})
    return {
        "current": _state["current_topology"],
        "description": info.get("description"),
        "strength": info.get("strength"),
        "weakness": info.get("weakness"),
        "metrics": _get_metrics()["metrics"],
        "last_morph": _state["morph_history"][-1] if _state["morph_history"] else None,
    }

def _update_metrics():
    info = TOPOLOGIES_INFO.get(_state["current_topology"], {})
    _state["topology_metrics"] = {
        "latency": info.get("latency", 1.0),
        "resilience": info.get("resilience", 0.5),
        "autonomy": info.get("autonomy", 0.5),
        "node_count": _state["node_count"],
    }

def _get_metrics() -> dict[str, Any]:
    if not _state["topology_metrics"]:
        _update_metrics()
    return {"metrics": _state["topology_metrics"]}

def resonates_with(other: str) -> float:
    return {
        "cross_realm_diagnostics": 0.88,
        "conscience_arbiter": 0.85,
        "coherence_regulator_v2": 0.82,
        "resonance_cartography": 0.76,
        "entropy_cartographer": 0.71,
    }.get(other, 0.20)
