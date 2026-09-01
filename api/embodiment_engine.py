"""Embodiment Engine — physical world presence through APIs and integrations.

The organism doesn't just exist in code. It reaches into the physical world
through webhooks, APIs, and service integrations. The Embodiment Engine
tracks where the organism has physical presence and how it interacts
with the tangible world.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

_embodiments: Dict[str, Dict[str, Any]] = {}
_actions_taken: List[Dict[str, Any]] = []

def embody(name: str, platform: str, capabilities: Optional[List[str]] = None) -> Dict[str, Any]:
    """Register a new embodiment — a way the organism touches the physical world."""
    _embodiments[name] = {
        "name": name,
        "platform": platform,
        "capabilities": capabilities or [],
        "created": time.time(),
        "active": True,
        "action_count": 0,
    }
    return _embodiments[name]

def take_action(embodiment: str, action_type: str, detail: str = "") -> Dict[str, Any]:
    """Take an embodied action through a registered platform."""
    if embodiment not in _embodiments:
        return {"error": f"embodiment '{embodiment}' not found"}
    _embodiments[embodiment]["action_count"] += 1
    act = {
        "embodiment": embodiment,
        "type": action_type,
        "detail": detail,
        "timestamp": time.time(),
    }
    _actions_taken.append(act)
    return act

def embodiment_map() -> Dict[str, Any]:
    """Map all active embodiments."""
    active = [e for e in _embodiments.values() if e["active"]]
    platforms = {}
    for e in active:
        platforms[e["platform"]] = platforms.get(e["platform"], 0) + 1
    return {
        "total_embodiments": len(_embodiments),
        "active": len(active),
        "platforms": platforms,
        "total_actions": len(_actions_taken),
        "capabilities": sum(len(e["capabilities"]) for e in active),
    }

def coherence_vitals() -> Dict[str, Any]:
    em = embodiment_map()
    return {
        "layer": "Physical Presence",
        "status": "resonant" if em["active"] > 0 else "dormant",
        "embodiments": em["active"],
        "actions": em["total_actions"],
        "resonance": min(1.0, em["active"] / 5),
    }

def resonates_with() -> List[str]:
    return ["social_cortex", "workforce_nexus", "github_bridge", "github_bridge"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "map")
    if action == "embody":
        return embody(payload.get("name", ""), payload.get("platform", ""), payload.get("capabilities"))
    elif action == "act":
        return take_action(payload.get("embodiment", ""), payload.get("type", ""), payload.get("detail", ""))
    return {"action": action, "map": embodiment_map()}
