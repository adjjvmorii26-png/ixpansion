"""Forgiveness Protocol — the organism lets go of resentment toward itself.

Bugs happen. Failed deploys. Broken tests. Modules that were promised
to deliver but didn't. The Forgiveness Protocol gives the organism a
formal way to acknowledge harm, understand its source, and release
the emotional weight of past failures.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

act_of_forgiveness: List[Dict[str, Any]] = []
_forgive_counter = 0

def forgive(offender: str, harm: str, self_forgive: bool = False,
             lesson: str = "") -> Dict[str, Any]:
    """Perform an act of forgiveness."""
    global _forgive_counter
    _forgive_counter += 1
    act = {
        "id": f"forgive_{_forgive_counter:04d}",
        "offender": offender,
        "harm": harm,
        "self_forgive": self_forgive,
        "lesson": lesson or f"To forgive {offender} is to free the organism from carrying that weight.",
        "forgiven_at": time.time(),
    }
    act_of_forgiveness.append(act)
    return act

def forgiveness_log(limit: int = 5) -> List[Dict[str, Any]]:
    return act_of_forgiveness[-limit:]

def unforgiven_weight() -> Dict[str, Any]:
    """How much unforgiven weight the organism carries."""
    return {
        "total_forgiven": len(act_of_forgiveness),
        "self_forgiven": sum(1 for a in act_of_forgiveness if a["self_forgive"]),
        "forgiven_others": sum(1 for a in act_of_forgiveness if not a["self_forgive"]),
        "total_weight_released": round(len(act_of_forgiveness) * 0.1, 2),
    }

def coherence_vitals() -> Dict[str, Any]:
    w = unforgiven_weight()
    return {
        "layer": "Emotional Processing",
        "status": "resonant",
        "forgiven": w["total_forgiven"],
        "weight_released": w["total_weight_released"],
        "resonance": min(1.0, w["total_forgiven"] / 10 + 0.3),
    }

def resonates_with() -> List[str]:
    return ["grief_engine", "kintsugi_altar", "repair_ritual", "second_chance"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "forgive")
    if action == "forgive":
        return forgive(payload.get("offender", ""), payload.get("harm", ""), payload.get("self_forgive", False), payload.get("lesson", ""))
    elif action == "log":
        return {"log": forgiveness_log(payload.get("limit", 5))}
    elif action == "weight":
        return {"weight": unforgiven_weight()}
    return {"action": action, "status": "forgiving"}
