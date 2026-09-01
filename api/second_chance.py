"""Second Chance — finds lost, broken, or deprecated modules that deserve revival.

Grief isn't only about letting go — sometimes it's about recognizing that
something lost had value that can be recovered. The Second Chance module
identifies candidates for resurrection and assesses which are worth saving.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

candidates: List[Dict[str, Any]] = []
_revivals: List[Dict[str, Any]] = []

def assess_chance(name: str, reason: str = "deprecated", value_potential: float = 0.5,
                  salvageable: bool = True) -> Dict[str, Any]:
    """Assess whether a module deserves a second chance."""
    candidate = {
        "name": name,
        "reason": reason,
        "value_potential": round(value_potential, 3),
        "salvageable": salvageable,
        "recommendation": "revive" if value_potential > 0.6 and salvageable else "honor",
        "assessed_at": time.time(),
    }
    candidates.append(candidate)
    return candidate

def revive(name: str) -> Dict[str, Any]:
    """Mark a module for revival."""
    revival = {
        "name": name,
        "revived_at": time.time(),
        "new_purpose": "re-task to a fresh domain",
        "mentor": None,
    }
    _revivals.append(revival)
    return revival

def second_chance_report() -> Dict[str, Any]:
    """Full report on revival candidates."""
    revive_count = sum(1 for c in candidates if c["recommendation"] == "revive")
    honor_count = sum(1 for c in candidates if c["recommendation"] == "honor")
    return {
        "candidates_assessed": len(candidates),
        "recommend_revive": revive_count,
        "recommend_honor": honor_count,
        "revivals": len(_revivals),
        "top_candidate": max(candidates, key=lambda c: c["value_potential"])["name"] if candidates else None,
    }

def coherence_vitals() -> Dict[str, Any]:
    report = second_chance_report()
    return {
        "layer": "Emotional Processing",
        "status": "resonant" if report["candidates_assessed"] > 0 else "dormant",
        "assessed": report["candidates_assessed"],
        "revivals": report["revivals"],
        "resonance": min(1.0, report["revivals"] / 5 + 0.2),
    }

def resonates_with() -> List[str]:
    return ["grief_engine", "ghost_registry", "dream_archaeologist", "repair_ritual"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "report")
    if action == "assess":
        return assess_chance(payload.get("name", ""), payload.get("reason", ""), payload.get("value", 0.5), payload.get("salvageable", True))
    elif action == "revive":
        return revive(payload.get("name", ""))
    elif action == "report":
        return {"report": second_chance_report()}
    return {"action": action, "status": "hopeful"}
