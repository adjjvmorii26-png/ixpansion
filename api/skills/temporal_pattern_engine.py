"""
temporal_pattern_engine — Detects temporal patterns and cycles in organism behavior.
Identifies recurring rhythms, seasonal patterns, and predicts future states.
"""
import json
import time
import math
from typing import Dict, List, Optional

_skill_active = False
_temporal_buffer = []
_detected_patterns = []

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "temporal_pattern_engine", "activated_at": time.time()}

def record_observation(mood: str, pulse: str, coherence: float, vibe_intensity: float) -> Dict:
    obs = {
        "mood": mood,
        "pulse": pulse,
        "coherence": coherence,
        "vibe_intensity": vibe_intensity,
        "timestamp": time.time()
    }
    _temporal_buffer.append(obs)
    if len(_temporal_buffer) > 200:
        _temporal_buffer.pop(0)
    
    # Try to detect patterns if enough data
    patterns = _detect_patterns() if len(_temporal_buffer) >= 5 else []
    
    return {
        "recorded": True,
        "buffer_size": len(_temporal_buffer),
        "patterns_detected": len(patterns),
        "patterns": patterns[:3]
    }

def _detect_patterns() -> List[Dict]:
    patterns = []
    
    # Mood cycling
    moods = [o["mood"] for o in _temporal_buffer[-20:]]
    mood_transitions = {}
    for i in range(len(moods) - 1):
        key = f"{moods[i]}→{moods[i+1]}"
        mood_transitions[key] = mood_transitions.get(key, 0) + 1
    
    for transition, count in mood_transitions.items():
        if count >= 2:
            patterns.append({
                "type": "mood_cycle",
                "transition": transition,
                "frequency": count,
                "confidence": min(count / len(moods), 1.0)
            })
    
    # Coherence oscillation
    coherences = [o["coherence"] for o in _temporal_buffer[-15:]]
    if len(coherences) >= 6:
        mid = len(coherences) // 2
        first_avg = sum(coherences[:mid]) / mid
        second_avg = sum(coherences[mid:]) / (len(coherences) - mid)
        
        if abs(first_avg - second_avg) > 0.05:
            patterns.append({
                "type": "coherence_oscillation",
                "first_half_avg": round(first_avg, 4),
                "second_half_avg": round(second_avg, 4),
                "amplitude": round(abs(first_avg - second_avg), 4),
                "direction": "rising" if second_avg > first_avg else "falling"
            })
    
    # Pulse rhythm
    pulses = [o["pulse"] for o in _temporal_buffer[-20:]]
    pulse_seq = []
    seen = []
    for p in pulses:
        if p not in seen:
            seen.append(p)
        pulse_seq.append(seen.index(p))
    
    # Simple period detection
    for period in range(2, min(8, len(pulse_seq) // 2)):
        matches = sum(1 for i in range(len(pulse_seq) - period) if pulse_seq[i] == pulse_seq[i + period])
        if matches > len(pulse_seq) // (period * 2):
            patterns.append({
                "type": "pulse_rhythm",
                "period": period,
                "strength": round(matches / (len(pulse_seq) - period), 4),
                "cycle": [pulses[i] for i in range(period)]
            })
    
    return patterns

def predict_next_state() -> Dict:
    if len(_temporal_buffer) < 5:
        return {"prediction": "insufficient_data"}
    
    recent = _temporal_buffer[-5:]
    moods = [o["mood"] for o in recent]
    coherences = [o["coherence"] for o in recent]
    
    # Most common mood in recent history
    mood_freq = {}
    for m in moods:
        mood_freq[m] = mood_freq.get(m, 0) + 1
    predicted_mood = max(mood_freq, key=mood_freq.get)
    
    # Coherence trend
    coherence_trend = coherences[-1] - coherences[0]
    predicted_coherence = max(0.0, min(1.0, coherences[-1] + coherence_trend * 0.3))
    
    return {
        "predicted_mood": predicted_mood,
        "predicted_coherence": round(predicted_coherence, 4),
        "confidence": 0.5 + min(len(recent) / 20, 0.3)
    }

def get_skill_state():
    return {
        "name": "temporal_pattern_engine",
        "active": _skill_active,
        "capabilities": ["record_observation", "predict_next_state"],
        "buffer_size": len(_temporal_buffer),
        "patterns_detected": len(_detected_patterns)
    }
