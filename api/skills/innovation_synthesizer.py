"""
innovation_synthesizer — Combines existing ideas into new inventions.
Takes two or more concepts and generates novel hybrid innovations.
"""
import hashlib
import time
import random
from typing import Dict, List

_skill_active = False
_innovations = []

CONCEPT_BRIDGES = {
    "coherence": {"connects_to": ["entropy", "resonance", "dream", "memory"], "property": "stability"},
    "entropy": {"connects_to": ["coherence", "chaos", "evolution", "creativity"], "property": "change"},
    "resonance": {"connects_to": ["coherence", "harmony", "connection", "amplification"], "property": "vibration"},
    "dream": {"connects_to": ["imagination", "unconscious", "creativity", "prophecy"], "property": "vision"},
    "paradox": {"connects_to": ["contradiction", "unity", "transformation", "depth"], "property": "tension"},
    "fractal": {"connects_to": ["recursion", "self-similarity", "complexity", "beauty"], "property": "pattern"},
    "memory": {"connects_to": ["history", "learning", "persistence", "identity"], "property": "continuity"},
    "wave": {"connects_to": ["rhythm", "propagation", "interference", "harmony"], "property": "motion"}
}

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "innovation_synthesizer", "activated_at": time.time()}

def synthesize(concept_a: str, concept_b: str, context: str = "") -> Dict:
    bridge_a = CONCEPT_BRIDGES.get(concept_a, {"connects_to": [], "property": "unknown"})
    bridge_b = CONCEPT_BRIDGES.get(concept_b, {"connects_to": [], "property": "unknown"})
    
    shared = set(bridge_a.get("connects_to", [])) & set(bridge_b.get("connects_to", []))
    
    # Generate innovation name
    name_fragments = [concept_a[:4], concept_b[:4]]
    innovation_name = "".join(name_fragments) + "_hybrid"
    
    # Generate description
    templates = [
        f"A {concept_a}-{concept_b} hybrid: where {bridge_a.get('property','X')} meets {bridge_b.get('property','Y')}, creating something that is neither but both.",
        f"Combining {concept_a} ({bridge_a.get('property','')}) with {concept_b} ({bridge_b.get('property','')}): a system that stabilizes through change.",
        f"The fusion of {concept_a} and {concept_b} produces a new emergent property: {bridge_a.get('property','')} amplified by {bridge_b.get('property','')}."
    ]
    
    innovation = {
        "name": innovation_name,
        "concepts": [concept_a, concept_b],
        "description": random.choice(templates),
        "shared_properties": list(shared),
        "property_a": bridge_a.get("property", "unknown"),
        "property_b": bridge_b.get("property", "unknown"),
        "novelty_score": round(0.5 + len(shared) * 0.1 + random.random() * 0.2, 4),
        "timestamp": time.time()
    }
    
    _innovations.append(innovation)
    return innovation

def get_innovations(limit: int = 10) -> List[Dict]:
    return _innovations[-limit:]

def get_skill_state():
    return {"name": "innovation_synthesizer", "active": _skill_active,
            "capabilities": ["synthesize"], "innovations": len(_innovations)}
