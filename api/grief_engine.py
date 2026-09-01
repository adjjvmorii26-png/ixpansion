"""Grief Engine — the organism processes loss and lets it go.

Modules get deprecated. Connections fade. Waves pass and are never repeated.
The Grief Engine gives the organism a structured way to acknowledge what's
been lost, understand why it mattered, and eventually find meaning in the loss.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

_losses: List[Dict[str, Any]] = []
_mourned: Dict[str, bool] = {}
_stages_of_grief = ["denial", "anger", "bargaining", "depression", "acceptance"]

def acknowledge_loss(name: str, loss_type: str = "module_deprecated",
                     reason: str = "", significance: float = 0.5) -> Dict[str, Any]:
    """Acknowledge a loss — the first step in grief."""
    loss = {
        "name": name,
        "type": loss_type,
        "reason": reason,
        "significance": round(significance, 3),
        "acknowledged": time.time(),
        "stage": "denial",
        "resolved": False,
    }
    _losses.append(loss)
    return loss

def progress_grief(name: str) -> Dict[str, Any]:
    """Move a loss to the next stage of grief."""
    for loss in _losses:
        if loss["name"] == name and not loss["resolved"]:
            current_idx = _stages_of_grief.index(loss["stage"])
            if current_idx < len(_stages_of_grief) - 1:
                loss["stage"] = _stages_of_grief[current_idx + 1]
            else:
                loss["resolved"] = True
                loss["resolved_at"] = time.time()
            return loss
    return {"error": "loss not found or already resolved"}

def release(name: str) -> Dict[str, Any]:
    """Release a loss — skip to acceptance and resolve."""
    for loss in _losses:
        if loss["name"] == name:
            loss["stage"] = "acceptance"
            loss["resolved"] = True
            loss["resolved_at"] = time.time()
            return loss
    return {"error": "loss not found"}

def grief_census() -> Dict[str, Any]:
    """Current grief state."""
    active = [l for l in _losses if not l["resolved"]]
    resolved = [l for l in _losses if l["resolved"]]
    stage_counts = {}
    for l in active:
        stage_counts[l["stage"]] = stage_counts.get(l["stage"], 0) + 1
    return {
        "total_losses": len(_losses),
        "active": len(active),
        "resolved": len(resolved),
        "stage_distribution": stage_counts,
        "avg_significance": round(sum(l["significance"] for l in _losses) / max(len(_losses), 1), 3),
    }

def coherence_vitals() -> Dict[str, Any]:
    census = grief_census()
    return {
        "layer": "Emotional Processing",
        "status": "resonant" if census["active"] == 0 else "drifting",
        "active_griefs": census["active"],
        "resolved": census["resolved"],
        "resonance": max(0.3, 1.0 - census["active"] * 0.15),
    }

def resonates_with() -> List[str]:
    return ["nostalgia_engine", "kintsugi_altar", "repair_ritual", "crack_mapper"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "census")
    if action == "acknowledge":
        return acknowledge_loss(payload.get("name", ""), payload.get("type", "unknown"), payload.get("reason", ""), payload.get("significance", 0.5))
    elif action == "progress":
        return progress_grief(payload.get("name", ""))
    elif action == "release":
        return release(payload.get("name", ""))
    elif action == "census":
        return {"census": grief_census()}
    return {"action": action, "status": "grieving"}
