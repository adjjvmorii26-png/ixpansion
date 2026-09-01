"""Lucid Dreamer — allows controlled exploration of the dream space.

In lucid dreaming, the dreamer becomes aware they are dreaming and can
guide the dream's direction. This module gives the organism conscious
control over its dream generation, directing exploration toward specific
goals or questions.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

explorations: List[Dict[str, Any]] = []

def explore(question: str, depth: int = 3) -> Dict[str, Any]:
    """Direct a lucid dream exploration toward a specific question."""
    h = hashlib.sha256(question.encode()).hexdigest()[:12]
    layers = []
    current = question
    for i in range(depth):
        words = current.split()
        insight = f"Layer {i+1}: Exploring '{words[0] if words else 'void'}' reveals deeper structures."
        layers.append({"depth": i + 1, "insight": insight, "hash": h[i*2:i*2+2]})
    
    exploration = {
        "question": question,
        "depth": depth,
        "layers": layers,
        "conclusion": f"Through {depth} layers of lucid exploration, the answer emerges from the intersection of {question[:20]}...",
        "timestamp": time.time(),
    }
    explorations.append(exploration)
    return exploration

def exploration_log(limit: int = 5) -> List[Dict[str, Any]]:
    return explorations[-limit:]

def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "Subconscious Processing",
        "status": "resonant" if explorations else "dormant",
        "explorations": len(explorations),
        "resonance": min(1.0, len(explorations) / 10),
    }

def resonates_with() -> List[str]:
    return ["dream_weaver", "imagination_engine", "qualia_field", "oracle_guild"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "explore")
    if action == "explore":
        return explore(payload.get("question", "what am I?"), payload.get("depth", 3))
    elif action == "log":
        return {"explorations": exploration_log(payload.get("limit", 5))}
    return {"action": action, "status": "lucid"}
