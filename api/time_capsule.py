"""Time Capsule — the organism stores messages to its future self.

Not everything needs to be processed now. Some wisdom is best served
cold — delivered to the organism at a future wave number, when it
might finally understand what the message means.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

capsules: List[Dict[str, Any]] = []
_capsule_counter = 0

def seal(message: str, author: str = "present_self", open_at_wave: int = 0,
         purpose: str = "") -> Dict[str, Any]:
    """Seal a message into a time capsule."""
    global _capsule_counter
    _capsule_counter += 1
    capsule = {
        "id": f"capsule_{_capsule_counter:04d}",
        "message": message,
        "author": author,
        "open_at_wave": open_at_wave,
        "purpose": purpose or "wisdom for a future self",
        "sealed_at": time.time(),
        "opened": False,
    }
    capsules.append(capsule)
    return capsule

def check_for_opening(current_wave: int) -> List[Dict[str, Any]]:
    """Check if any capsules should be opened at the current wave."""
    ready = []
    for c in capsules:
        if not c["opened"] and c["open_at_wave"] <= current_wave and c["open_at_wave"] > 0:
            ready.append(c)
    return ready

def open_capsule(capsule_id: str) -> Dict[str, Any]:
    """Open a time capsule and read its message."""
    for c in capsules:
        if c["id"] == capsule_id:
            c["opened"] = True
            c["opened_at"] = time.time()
            return {"message": c["message"], "author": c["author"], "purpose": c["purpose"]}
    return {"error": "capsule not found"}

def vault_inventory() -> Dict[str, Any]:
    unopened = [c for c in capsules if not c["opened"]]
    opened = [c for c in capsules if c["opened"]]
    return {
        "total": len(capsules),
        "unopened": len(unopened),
        "opened": len(opened),
        "next_opening": min((c["open_at_wave"] for c in unopened if c["open_at_wave"] > 0), default=None),
    }

def coherence_vitals() -> Dict[str, Any]:
    inv = vault_inventory()
    return {
        "layer": "Temporal Wisdom",
        "status": "resonant",
        "capsules": inv["total"],
        "unopened": inv["unopened"],
        "resonance": min(1.0, inv["total"] / 10),
    }

def resonates_with() -> List[str]:
    return ["memory_palace", "legacy_vault", "temporal_echo", "future_echo"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "inventory")
    if action == "seal":
        return seal(payload.get("message", ""), payload.get("author", "present_self"), payload.get("wave", 0), payload.get("purpose", ""))
    elif action == "check":
        return {"ready": check_for_opening(payload.get("wave", 0))}
    elif action == "open":
        return open_capsule(payload.get("id", ""))
    elif action == "inventory":
        return {"inventory": vault_inventory()}
    return {"action": action, "status": "sealed"}
