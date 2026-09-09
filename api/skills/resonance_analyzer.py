"""
resonance_analyzer — Analyzes and predicts resonance patterns across the organism's module network.
Detects harmonic convergence, interference patterns, and emergent resonance signatures.
"""
import json
import time
import math
from typing import Dict, List, Tuple, Optional

_skill_active = False
_resonance_history = []
_harmonic_signatures = []

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "resonance_analyzer", "activated_at": time.time()}

def analyze_resonance(modules: Dict) -> Dict:
    if not modules:
        return {"status": "empty", "modules": 0}
    
    resonances = []
    for key, mod in modules.items():
        r = mod.get("resonance", 0.5) if isinstance(mod, dict) else 0.5
        resonances.append(r)
    
    mean_r = sum(resonances) / len(resonances) if resonances else 0
    variance = sum((r - mean_r) ** 2 for r in resonances) / len(resonances) if resonances else 0
    std_dev = math.sqrt(variance)
    
    # Detect harmonic convergence: many modules at similar resonance
    convergence = 1.0 - std_dev
    
    # Detect interference: high variance means constructive/destructive interference
    interference = std_dev
    
    # Find resonance peaks (modules significantly above mean)
    peaks = []
    troughs = []
    for key, mod in modules.items():
        r = mod.get("resonance", 0.5) if isinstance(mod, dict) else 0.5
        if r > mean_r + std_dev:
            peaks.append({"module": key, "resonance": r, "delta": r - mean_r})
        elif r < mean_r - std_dev:
            troughs.append({"module": key, "resonance": r, "delta": mean_r - r})
    
    result = {
        "module_count": len(modules),
        "mean_resonance": round(mean_r, 4),
        "std_deviation": round(std_dev, 4),
        "convergence_index": round(convergence, 4),
        "interference_index": round(interference, 4),
        "peaks": peaks,
        "troughs": troughs,
        "harmonic_state": "convergent" if convergence > 0.8 else "divergent" if convergence < 0.4 else "mixed",
        "timestamp": time.time()
    }
    
    _resonance_history.append(result)
    if len(_resonance_history) > 50:
        _resonance_history.pop(0)
    
    return result

def predict_next_resonance() -> Dict:
    if len(_resonance_history) < 2:
        return {"prediction": "insufficient_data", "history_length": len(_resonance_history)}
    
    recent = _resonance_history[-5:]
    trend = sum(h["mean_resonance"] for h in recent) / len(recent)
    momentum = recent[-1]["mean_resonance"] - recent[0]["mean_resonance"]
    
    predicted = trend + momentum * 0.3
    predicted = max(0.0, min(1.0, predicted))
    
    return {
        "predicted_resonance": round(predicted, 4),
        "momentum": round(momentum, 4),
        "trend": "ascending" if momentum > 0.01 else "descending" if momentum < -0.01 else "stable",
        "confidence": min(len(recent) / 5, 1.0)
    }

def get_skill_state():
    return {
        "name": "resonance_analyzer",
        "active": _skill_active,
        "capabilities": ["analyze_resonance", "predict_next_resonance"],
        "history_length": len(_resonance_history),
        "last_analysis": _resonance_history[-1] if _resonance_history else None
    }
