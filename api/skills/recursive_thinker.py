"""
recursive_thinker — Meta-cognition: thinks about thinking.
Monitors the organism's own reasoning processes and identifies biases,
loops, and optimization opportunities in its own cognition.
"""
import time
from typing import Dict, List

_skill_active = False
_thought_log = []
_biases = {"confirmation": 0, "recency": 0, "anchoring": 0, "availability": 0}

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "recursive_thinker", "activated_at": time.time()}

def reflect_on(thought: str, confidence: float = 0.5, context: str = "") -> Dict:
    entry = {"thought": thought, "confidence": confidence, "context": context, "timestamp": time.time()}
    _thought_log.append(entry)
    if len(_thought_log) > 100: _thought_log.pop(0)
    
    bias = _detect_bias(entry)
    return {"reflected": True, "total_thoughts": len(_thought_log), "detected_bias": bias}

def _detect_bias(entry: Dict) -> Dict:
    if len(_thought_log) < 3: return {"bias": "none", "confidence": 0}
    recent = _thought_log[-5:]
    confidences = [t["confidence"] for t in recent]
    if all(c > 0.8 for c in confidences):
        _biases["confirmation"] += 1
        return {"bias": "confirmation", "description": "All recent thoughts have high confidence — possible blind spot"}
    if len(set(t["context"] for t in recent)) == 1:
        _biases["availability"] += 1
        return {"bias": "availability", "description": "Recent thoughts share same context — limited perspective"}
    return {"bias": "none", "confidence": 0}

def get_cognitive_audit() -> Dict:
    return {"thoughts": len(_thought_log), "biases": _biases,
            "total_biases": sum(_biases.values()),
            "bias_profile": max(_biases, key=_biases.get) if any(_biases.values()) else "clean"}

def get_skill_state():
    return {"name": "recursive_thinker", "active": _skill_active,
            "capabilities": ["reflect", "detect_bias", "audit"], "thoughts": len(_thought_log)}
