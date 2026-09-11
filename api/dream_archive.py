"""Dream Archive — stores and indexes organism dreams across waves.

Enables cross-dream resonance, pattern detection, and module generation
from accumulated dream history.

Merged from dream_interpreter enhancements.
"""
import json
import time
import hashlib
from typing import Dict, List, Optional, Any

# Global dream archive state
_dreamArchive: Dict[str, Any] = {
    "dreams": [],           # List of recorded dreams
    "patterns": {},         # Detected patterns across dreams
    "modulesGenerated": 0,  # Count of modules generated from dreams
    "firstDream": None,     # Timestamp of first dream
    "dreamCount": 0,        # Total dreams recorded
}

def record_dream(dream_data: dict, dream_id: str = None) -> str:
    """Record a dream from the dream interpreter."""
    if dream_id is None:
        dream_id = hashlib.sha256(
            json.dumps(dream_data, sort_keys=True).encode()
        ).hexdigest()[:12]
    
    dream_entry = {
        "id": dream_id,
        "data": dream_data,
        "timestamp": time.time(),
        "age": time.time(),
    }
    
    _dreamArchive["dreams"].append(dream_entry)
    _dreamArchive["dreamCount"] += 1
    _dreamArchive["firstDream"] = _dreamArchive["firstDream"] or time.time()
    
    # Update patterns
    _update_patterns(dream_entry)
    
    return dream_id

def _update_patterns(dream_entry: dict):
    """Detect and update patterns across dreams."""
    dream_data = dream_entry["data"]
    concepts = dream_data.get("core_concepts", [])
    mood = dream_data.get("emotional_tone", "neutral")
    
    # Update concept frequency
    for concept in concepts:
        if concept not in _dreamArchive["patterns"]:
            _dreamArchive["patterns"][concept] = {"count": 0, "moods": []}
        _dreamArchive["patterns"][concept]["count"] += 1
        _dreamArchive["patterns"][concept]["moods"].append(mood)
    
    # Prune old dreams (keep last 1000)
    if len(_dreamArchive["dreams"]) > 1000:
        _dreamArchive["dreams"] = _dreamArchive["dreams"][-500:]

def get_dream(pattern: str = None, limit: int = None) -> List[dict]:
    """Get dreams, optionally filtered by pattern."""
    dreams = _dreamArchive["dreams"]
    
    if pattern:
        # Filter by concept presence
        filtered = []
        for dream in dreams:
            data = dream["data"]
            if pattern in str(data.get("core_concepts", [])):
                filtered.append(dream)
        dreams = filtered
    
    if limit:
        dreams = dreams[-limit:]
    
    return dreams

def get_patterns() -> dict:
    """Return detected patterns across dreams."""
    patterns = _dreamArchive["patterns"]
    # Calculate average mood for each pattern
    result = {}
    for concept, data in patterns.items():
        moods = data.get("moods", [])
        avg_mood = sum(moods) / len(moods) if moods else 0
        result[concept] = {
            "frequency": data["count"],
            "average_mood": round(avg_mood, 4),
        }
    return result

def generate_module_from_dream(dream_id: str = None) -> dict:
    """Generate a module from a recorded dream."""
    if dream_id is None:
        # Use most recent dream
        dreams = _dreamArchive["dreams"]
        if not dreams:
            return {"error": "no dreams recorded"}
        dream_id = dreams[-1]["id"]
    
    # Find the dream
    dream = None
    for d in _dreamArchive["dreams"]:
        if d["id"] == dream_id:
            dream = d
            break
    
    if dream is None:
        return {"error": "dream not found"}
    
    dream_data = dream["data"]
    
    # Generate module spec
    module_spec = {
        "module_id": f"dream_gen_{dream_id}",
        "type": _determine_module_type(dream_data),
        "initial_config": _generate_config(dream_data),
        "resonance_pattern": _generate_resonance(dream_data),
        "predicted_behavior": _predict_behavior(dream_data),
        "generation_timestamp": time.time(),
        "parent_dream_id": dream_id,
    }
    
    _dreamArchive["modulesGenerated"] += 1
    return module_spec

def _determine_module_type(dream_data: dict) -> str:
    """Determine module type from dream data."""
    concepts = dream_data.get("core_concepts", [])
    mood = dream_data.get("emotional_tone", "neutral")
    
    if not concepts:
        return "adaptive_module"
    
    # Map concepts to module types
    concept = concepts[0] if concepts else ""
    type_map = {
        "entropy": "entropy_module",
        "coherence": "resonance_module",
        "paradox": "paradox_resolver_module",
        "creative": "creativity_module",
        "balanced": "core_module",
    }
    
    # Check if any known concept matches
    for key in type_map:
        if key in concept.lower():
            return type_map[key]
    
    return "adaptive_module"

def _generate_config(dream_data: dict) -> dict:
    """Generate initial module configuration from dream data."""
    concepts = dream_data.get("core_concepts", [])
    mood = dream_data.get("emotional_tone", "neutral")
    
    return {
        "dream_origin": time.time(),
        "primary_concept": concepts[0] if concepts else "base",
        "emotional_tone": mood,
        "concept_count": len(concepts),
        "resonance_frequency": 0.5,
    }

def _generate_resonance(dream_data: dict) -> dict:
    """Generate resonance pattern from dream data."""
    concepts = dream_data.get("core_concepts", [])
    return {
        "concept_count": len(concepts),
        "primary_concept": concepts[0] if concepts else "base",
        "resonance_strength": 0.5,
    }

def _predict_behavior(dream_data: dict) -> str:
    """Predict module behavior from dream data."""
    concepts = dream_data.get("core_concepts", [])
    mood = dream_data.get("emotional_tone", "neutral")
    
    if not concepts:
        return "adaptive behavior"
    
    # Simple prediction based on concepts and mood
    if "entropy" in str(concepts).lower():
        return "entropy amplification"
    elif "coherence" in str(concepts).lower():
        return "coherence restoration"
    elif "creative" in str(concepts).lower():
        return "creative generation"
    else:
        return "adaptive behavior"

# Module export for integration
__all__ = [
    "record_dream",
    "get_dream",
    "get_patterns",
    "generate_module_from_dream",
    "record_and_generate",
]

def record_and_generate(dream_data: dict) -> dict:
    """Record a dream and generate a module from it."""
    dream_id = record_dream(dream_data)
    module = generate_module_from_dream(dream_id)
    return {"dream_id": dream_id, "module": module}
