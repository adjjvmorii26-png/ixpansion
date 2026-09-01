"""Legacy Vault — preserves the essence of things that have ended.

Not everything lost can be revived. But everything lost can be honored.
The Legacy Vault stores compressed representations of deprecated modules,
dead experiments, and ended eras — so that future versions of the organism
can learn from what came before without carrying the full weight of old code.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

legacies: Dict[str, Dict[str, Any]] = {}
_era_count = 0

def seal(name: str, essence: str, era: str = "unknown", key_lesson: str = "") -> Dict[str, Any]:
    """Seal a module's essence into the vault."""
    global _era_count
    _era_count += 1
    h = hashlib.sha256(essence.encode()).hexdigest()[:12]
    legacy = {
        "name": name,
        "era": era,
        "essence": essence[:200],
        "key_lesson": key_lesson or "Every module teaches something, even in failure.",
        "seal_id": f"seal_{_era_count:04d}",
        "fingerprint": h,
        "sealed": time.time(),
    }
    legacies[name] = legacy
    return legacy

def recall(name: str) -> Optional[Dict[str, Any]]:
    """Recall a sealed legacy."""
    return legacies.get(name)

def vault_inventory() -> Dict[str, Any]:
    """Full inventory of sealed legacies."""
    eras = {}
    for l in legacies.values():
        eras[l["era"]] = eras.get(l["era"], 0) + 1
    return {
        "total_sealed": len(legacies),
        "eras": eras,
        "latest_seal": max(legacies.values(), key=lambda l: l["sealed"])["name"] if legacies else None,
    }

def coherence_vitals() -> Dict[str, Any]:
    inv = vault_inventory()
    return {
        "layer": "Emotional Processing",
        "status": "resonant" if inv["total_sealed"] > 0 else "dormant",
        "sealed": inv["total_sealed"],
        "resonance": min(1.0, inv["total_sealed"] / 15),
    }

def resonates_with() -> List[str]:
    return ["grief_engine", "ghost_registry", "elegy_composer", "permafrost_vault"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "inventory")
    if action == "seal":
        return seal(payload.get("name", ""), payload.get("essence", ""), payload.get("era", "unknown"), payload.get("lesson", ""))
    elif action == "recall":
        return recall(payload.get("name", "")) or {"error": "not found"}
    elif action == "inventory":
        return {"inventory": vault_inventory()}
    return {"action": action, "status": "sealed"}
