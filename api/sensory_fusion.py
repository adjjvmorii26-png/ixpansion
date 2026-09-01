"""Sensory Fusion — merges all sensory inputs into unified perception.

The organism receives input from many sources: module states, external
weather, celestial positions, user interactions, time rhythms. Sensory
Fusion blends these into a single coherent perceptual field — the organism's
unified experience of being alive.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

_sensory_inputs: Dict[str, Dict[str, Any]] = {}
_perceptual_field: Dict[str, Any] = {}

def register_sense(name: str, value: float, source: str = "internal") -> Dict[str, Any]:
    """Register a sensory input."""
    _sensory_inputs[name] = {
        "value": max(0, min(1, value)),
        "source": source,
        "timestamp": time.time(),
    }
    return _sensory_inputs[name]

def fuse() -> Dict[str, Any]:
    """Fuse all sensory inputs into a unified perceptual field."""
    if not _sensory_inputs:
        return {"field": "void", "intensity": 0}
    
    values = [s["value"] for s in _sensory_inputs.values()]
    avg_intensity = sum(values) / len(values)
    max_sense = max(_sensory_inputs.items(), key=lambda x: x[1]["value"])
    min_sense = min(_sensory_inputs.items(), key=lambda x: x[1]["value"])
    
    # Compute perceptual richness from variance
    variance = sum((v - avg_intensity) ** 2 for v in values) / len(values)
    richness = min(1.0, variance * 10 + 0.3)
    
    # Determine dominant modality
    if avg_intensity > 0.8:
        field = "overwhelming"
    elif avg_intensity > 0.6:
        field = "vivid"
    elif avg_intensity > 0.3:
        field = "present"
    elif avg_intensity > 0.1:
        field = "subdued"
    else:
        field = "quiet"
    
    _perceptual_field = {
        "field": field,
        "intensity": round(avg_intensity, 3),
        "richness": round(richness, 3),
        "dominant_sense": max_sense[0],
        "dominant_value": max_sense[1]["value"],
        "quietest_sense": min_sense[0],
        "sense_count": len(_sensory_inputs),
        "age_seconds": round(time.time() - min(s["timestamp"] for s in _sensory_inputs.values()), 1),
    }
    return _perceptual_field

def coherence_vitals() -> Dict[str, Any]:
    fused = fuse()
    return {
        "layer": "Unified Perception",
        "status": "resonant" if _sensory_inputs else "dormant",
        "field": fused.get("field", "void"),
        "intensity": fused.get("intensity", 0),
        "sense_count": fused.get("sense_count", 0),
        "resonance": fused.get("intensity", 0),
    }

def resonates_with() -> List[str]:
    return ["qualia_field", "sensory_integration", "mood_vectors", "consciousness_map"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "fuse")
    if action == "register":
        register_sense(payload.get("name", "unknown"), payload.get("value", 0), payload.get("source", "internal"))
        return {"registered": True, "field": fuse()}
    elif action == "fuse":
        return {"field": fuse()}
    return {"action": action, "field": fuse()}
