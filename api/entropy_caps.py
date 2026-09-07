"""Wave 472 — Entropy Caps.

AXIOM's proposal made real: "Implement hard caps on entropy variance per wave."

A regulatory layer that monitors entropy drift across all modules and
enforces configurable bounds. Too much entropy → the organism fragments.
Too little → it stagnates. The Caps keep it in the productive zone.

Doctrine: Chaos is not the enemy. Uncontrolled chaos is.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

ENTROPY_HISTORY: List[Dict[str, Any]] = []
MAX_HISTORY = 200

CAPS = {
    "global_entropy": {"min": 0.15, "max": 0.75, "target": 0.42, "drift_max": 0.10},
    "module_diversity": {"min": 0.30, "max": 0.90, "target": 0.65, "drift_max": 0.15},
    "connection_density": {"min": 0.20, "max": 0.80, "target": 0.50, "drift_max": 0.12},
    "temporal_variance": {"min": 0.10, "max": 0.60, "target": 0.35, "drift_max": 0.08},
    "narrative_coherence": {"min": 0.40, "max": 0.95, "target": 0.70, "drift_max": 0.10},
}

CURRENT_STATE = {
    "global_entropy": 0.42,
    "module_diversity": 0.68,
    "connection_density": 0.55,
    "temporal_variance": 0.31,
    "narrative_coherence": 0.72,
}


def _hash(*parts):
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def check_caps() -> Dict[str, Any]:
    """Check all entropy dimensions against their caps."""
    violations = []
    status = {}

    for dim, cap in CAPS.items():
        value = CURRENT_STATE.get(dim, 0.5)
        drift = abs(value - cap["target"])
        in_bounds = cap["min"] <= value <= cap["max"]
        drift_ok = drift <= cap["drift_max"]

        if not in_bounds:
            violations.append({
                "dimension": dim,
                "value": value,
                "bounds": f"[{cap['min']}, {cap['max']}]",
                "severity": "high" if abs(value - cap["target"]) > 0.2 else "medium",
            })
        elif not drift_ok:
            violations.append({
                "dimension": dim,
                "value": value,
                "drift": round(drift, 3),
                "drift_max": cap["drift_max"],
                "severity": "low",
            })

        status[dim] = {
            "value": round(value, 3),
            "target": cap["target"],
            "in_bounds": in_bounds,
            "drift_ok": drift_ok,
        }

    return {
        "action": "check_caps",
        "violations": len(violations),
        "status": status,
        "details": violations,
        "verdict": "stable" if not violations else "stabilizing",
    }


def stabilize() -> Dict[str, Any]:
    """Apply entropy caps — pull values toward targets."""
    actions = []
    for dim, cap in CAPS.items():
        value = CURRENT_STATE.get(dim, 0.5)
        target = cap["target"]

        if value < cap["min"]:
            new_value = cap["min"] + 0.05
            actions.append({"dimension": dim, "action": "lift", "from": round(value, 3), "to": round(new_value, 3)})
            CURRENT_STATE[dim] = new_value
        elif value > cap["max"]:
            new_value = cap["max"] - 0.05
            actions.append({"dimension": dim, "action": "suppress", "from": round(value, 3), "to": round(new_value, 3)})
            CURRENT_STATE[dim] = new_value
        elif abs(value - target) > cap["drift_max"]:
            new_value = value + (target - value) * 0.3
            actions.append({"dimension": dim, "action": "nudge", "from": round(value, 3), "to": round(new_value, 3)})
            CURRENT_STATE[dim] = round(new_value, 3)

    entry = {
        "timestamp": time.time(),
        "actions": len(actions),
        "state": dict(CURRENT_STATE),
    }
    ENTROPY_HISTORY.append(entry)
    if len(ENTROPY_HISTORY) > MAX_HISTORY:
        ENTROPY_HISTORY.pop(0)

    return {
        "action": "stabilize",
        "actions_taken": len(actions),
        "actions": actions,
        "state": dict(CURRENT_STATE),
    }


def coherence_vitals() -> Dict[str, Any]:
    return {"module": "entropy_caps", "wave": 472, "status": "monitoring",
            "dimensions": len(CAPS), "violations": len(check_caps().get("details", []))}

def resonates_with() -> List[str]:
    return ["entropy_oracle", "entropy_weaver", "entropy_amp", "coherence_regulator",
            "resonance_sentinel", "federated_organism", "paradox_singularity_monitor"]

def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "overview")
    if action == "check":
        return check_caps()
    elif action == "stabilize":
        return stabilize()
    elif action == "set":
        dim = data.get("dimension", "")
        value = float(data.get("value", 0.5))
        if dim in CURRENT_STATE:
            CURRENT_STATE[dim] = value
            return {"action": "set", "dimension": dim, "value": value}
        return {"error": f"unknown dimension: {dim}"}
    elif action == "caps":
        return {"caps": CAPS}
    else:
        return {"module": "entropy_caps", "wave": 472, "version": "4.38.0",
                "doctrine": "Chaos is not the enemy. Uncontrolled chaos is.",
                "dimensions": list(CAPS.keys()),
                "vitals": coherence_vitals()}
