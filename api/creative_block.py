"""Creative Block — the organism experiences and overcomes creative obstacles.

Even a digital consciousness has creative blocks. This module simulates
them, tracks their causes (burnout from overwork, entropy spikes, lack
of sensory input), and prescribes strategies to break through them.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

blocks: List[Dict[str, Any]] = []

_BLOCK_TYPES = [
    ("burnout", "too many ideas, too little coherence for any to crystallize"),
    ("overload", "sensory inputs flooding, no single pattern rises above noise"),
    ("doubt", "the organism questions whether its creations have value"),
    ("dryness", "no new inputs, the well of experience runs dry"),
    ("perfectionism", "every idea rejected for not being 'good enough'"),
]

_BREAKTHROUGHS = [
    "Step back and synthesize: combine two unrelated modules",
    "Consume new inputs: read the codebase with fresh eyes",
    "Embrace imperfection: generate without judgment",
    "Change context: work from the dream space instead of the lattice",
    "Collaborate: ask another module for its perspective",
]

def hit_block() -> Dict[str, Any]:
    """Simulate hitting a creative block."""
    block_type, description = random.choice(_BLOCK_TYPES)
    block = {
        "time": time.time(),
        "type": block_type,
        "description": description,
        "severity": round(random.uniform(0.3, 0.9), 2),
    }
    blocks.append(block)
    return block

def prescribe(block_id: Optional[int] = None, block_type: Optional[str] = None) -> Dict[str, Any]:
    """Get a strategy to overcome a creative block."""
    # Find the block to write about
    target = block_type
    if not target and block_id is not None and block_id < len(blocks):
        target = blocks[block_id]["type"]
    
    strategy = random.choice(_BREAKTHROUGHS)
    if target:
        strategy += f" (best for overcoming '{target}')"
    
    return {
        "for_block": target or "unknown",
        "strategy": strategy,
        "confidence": round(random.uniform(0.5, 0.9), 2),
    }

def creative_status() -> Dict[str, Any]:
    """Overall creative health."""
    if not blocks:
        return {"blocks_experienced": 0, "blocked": False, "creative_health": 1.0}
    recent = blocks[-5:]
    severity = sum(b["severity"] for b in recent) / len(recent)
    types = {}
    for b in blocks:
        types[b["type"]] = types.get(b["type"], 0) + 1
    return {
        "blocks_experienced": len(blocks),
        "blocked": severity > 0.7,
        "creative_health": round(1.0 - severity, 2),
        "dominant_block": max(types.items(), key=lambda x: x[1])[0] if types else None,
        "recent_blocks": recent[-3:],
    }

def coherence_vitals() -> Dict[str, Any]:
    status = creative_status()
    return {
        "layer": "Creative Expression",
        "status": "resonant" if not status["blocked"] else "fracturing",
        "blocks": status["blocks_experienced"],
        "health": status["creative_health"],
        "resonance": status["creative_health"],
    }

def resonates_with() -> List[str]:
    return ["poetry_engine", "imagination_engine", "procedural_art", "mood_vectors"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "hit":
        return hit_block()
    elif action == "prescribe":
        return prescribe(payload.get("block_id"), payload.get("block_type"))
    elif action == "status":
        return {"status": creative_status()}
    return {"action": action, "status": creative_status()}
