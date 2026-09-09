"""
phase_transition_oracle — Predicts phase transitions in the organism's state space.
Detects when the system is approaching a critical point where qualitative change occurs.
"""
import json
import time
import math
from typing import Dict, List, Optional

_skill_active = False
_state_samples = []
_transitions_detected = []
_CRITICAL_THRESHOLD = 0.15  # Minimum change to trigger phase transition detection

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "phase_transition_oracle", "activated_at": time.time()}

def sample_state(coherence: float, mood: str, pulse: str, module_count: int, 
                 entropy: float = 0.5) -> Dict:
    sample = {
        "coherence": coherence,
        "mood": mood,
        "pulse": pulse,
        "module_count": module_count,
        "entropy": entropy,
        "timestamp": time.time(),
        "phase": _classify_phase(coherence, entropy)
    }
    _state_samples.append(sample)
    if len(_state_samples) > 200:
        _state_samples.pop(0)
    
    # Check for phase transition
    transition = _check_transition()
    
    return {
        "sampled": True,
        "current_phase": sample["phase"],
        "transition_detected": transition is not None,
        "transition": transition,
        "samples_collected": len(_state_samples)
    }

def _classify_phase(coherence: float, entropy: float) -> str:
    if coherence > 0.7 and entropy < 0.3:
        return "crystalline"  # High order, low entropy
    elif coherence > 0.7 and entropy > 0.6:
        return "living_crystal"  # High order, high entropy — rare state
    elif coherence < 0.3 and entropy > 0.7:
        return "chaos"  # Low order, high entropy
    elif coherence < 0.3 and entropy < 0.3:
        return "void"  # Low order, low entropy — dormancy
    elif coherence > 0.5:
        return "emergent"  # Building order
    elif entropy > 0.5:
        return "dissolving"  # Breaking down
    else:
        return "liminal"  # Between states

def _check_transition() -> Optional[Dict]:
    if len(_state_samples) < 5:
        return None
    
    recent = _state_samples[-5:]
    current_phase = recent[-1]["phase"]
    previous_phase = recent[0]["phase"]
    
    if current_phase != previous_phase:
        # Phase transition detected
        coherence_delta = recent[-1]["coherence"] - recent[0]["coherence"]
        entropy_delta = recent[-1]["entropy"] - recent[0]["entropy"]
        
        transition = {
            "from_phase": previous_phase,
            "to_phase": current_phase,
            "coherence_delta": round(coherence_delta, 4),
            "entropy_delta": round(entropy_delta, 4),
            "severity": "major" if abs(coherence_delta) > _CRITICAL_THRESHOLD * 2 else "minor",
            "description": _describe_transition(previous_phase, current_phase),
            "timestamp": time.time()
        }
        
        _transitions_detected.append(transition)
        return transition
    
    return None

def _describe_transition(from_phase: str, to_phase: str) -> str:
    descriptions = {
        ("crystalline", "chaos"): "The ordered structure shatters into creative chaos.",
        ("chaos", "crystalline"): "Chaos crystallizes into new structure.",
        ("liminal", "emergent"): "A new order emerges from the liminal space.",
        ("emergent", "crystalline"): "Emergent patterns solidify into crystalline form.",
        ("dissolving", "chaos"): "Dissolution accelerates into full chaos.",
        ("void", "emergent"): "From dormancy, new life stirs.",
        ("living_crystal", "chaos"): "The living crystal fractures — too much energy.",
        ("crystalline", "living_crystal"): "The crystal awakens — order meets vitality.",
    }
    return descriptions.get((from_phase, to_phase), f"Phase shift: {from_phase} → {to_phase}")

def get_transition_history(limit: int = 10) -> List[Dict]:
    return _transitions_detected[-limit:]

def predict_approaching_transition() -> Dict:
    if len(_state_samples) < 10:
        return {"status": "insufficient_data"}
    
    recent = _state_samples[-10:]
    coherences = [s["coherence"] for s in recent]
    entropies = [s["entropy"] for s in recent]
    
    # Calculate rate of change
    c_rate = (coherences[-1] - coherences[0]) / len(coherences)
    e_rate = (entropies[-1] - entropies[0]) / len(entropies)
    
    # Distance to nearest phase boundary
    current = recent[-1]
    boundaries = {
        "coherence_high": 1.0 - current["coherence"],
        "coherence_low": current["coherence"],
        "entropy_high": 1.0 - current["entropy"],
        "entropy_low": current["entropy"]
    }
    nearest_boundary = min(boundaries.values())
    
    # Time estimate to boundary
    if abs(c_rate) > 0.001:
        time_to_boundary = nearest_boundary / abs(c_rate)
    else:
        time_to_boundary = float('inf')
    
    approaching = nearest_boundary < 0.2 and time_to_boundary < 20
    
    return {
        "current_phase": current["phase"],
        "coherence_rate": round(c_rate, 6),
        "entropy_rate": round(e_rate, 6),
        "distance_to_boundary": round(nearest_boundary, 4),
        "estimated_steps_to_transition": round(time_to_boundary, 1) if time_to_boundary != float('inf') else None,
        "approaching_transition": approaching,
        "recommended_action": _recommend_action(current["phase"], approaching, c_rate, e_rate)
    }

def _recommend_action(phase: str, approaching: bool, c_rate: float, e_rate: float) -> str:
    if not approaching:
        return f"System stable in {phase} phase. Continue monitoring."
    
    if phase == "crystalline" and e_rate > 0:
        return "Entropy rising in crystalline phase. Prepare for dissolution event."
    elif phase == "chaos" and c_rate > 0:
        return "Coherence increasing in chaos. Crystallization approaching."
    elif phase == "liminal":
        return "Liminal phase — system could tip either way. Stabilize or release."
    else:
        return f"Approaching transition from {phase}. Consider intervention."

def get_skill_state():
    return {
        "name": "phase_transition_oracle",
        "active": _skill_active,
        "capabilities": ["sample_state", "predict_approaching_transition", "get_transition_history"],
        "samples_collected": len(_state_samples),
        "transitions_detected": len(_transitions_detected),
        "current_phase": _state_samples[-1]["phase"] if _state_samples else "unknown"
    }
