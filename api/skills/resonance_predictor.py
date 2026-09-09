"""
resonance_predictor — Forecasts future resonance patterns using momentum and harmonic analysis.
Predicts convergence, divergence, and critical resonance events.
"""
import math
import time
from typing import Dict, List, Optional

_skill_active = False
_resonance_history = []
_predictions = []

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "resonance_predictor", "activated_at": time.time()}

def record_resonance(mean_resonance: float, peak_count: int = 0, 
                     trough_count: int = 0, convergence: float = 0.5) -> Dict:
    sample = {
        "mean": mean_resonance,
        "peaks": peak_count,
        "troughs": trough_count,
        "convergence": convergence,
        "timestamp": time.time()
    }
    _resonance_history.append(sample)
    if len(_resonance_history) > 100:
        _resonance_history.pop(0)
    
    prediction = _predict() if len(_resonance_history) >= 5 else None
    if prediction:
        _predictions.append(prediction)
    
    return {
        "recorded": True,
        "history_length": len(_resonance_history),
        "prediction": prediction
    }

def _predict() -> Optional[Dict]:
    if len(_resonance_history) < 5:
        return None
    
    recent = _resonance_history[-10:]
    values = [r["mean"] for r in recent]
    
    # Momentum
    momentum = values[-1] - values[0]
    
    # Acceleration (second derivative)
    if len(values) >= 3:
        accel = (values[-1] - values[-2]) - (values[-2] - values[-3])
    else:
        accel = 0
    
    # Predicted next value
    predicted = values[-1] + momentum * 0.3 + accel * 0.1
    predicted = max(0.0, min(1.0, predicted))
    
    # Convergence trend
    convergences = [r["convergence"] for r in recent]
    conv_trend = convergences[-1] - convergences[0] if convergences else 0
    
    # Harmonic frequency (simple peak detection)
    peak_intervals = []
    for i in range(1, len(values)):
        if values[i] > values[i-1] and (i == 1 or values[i-1] <= values[i-2]):
            peak_intervals.append(i)
    
    harmonic_freq = len(peak_intervals) / max(len(values) - 1, 1)
    
    # Event detection
    events = []
    if abs(momentum) > 0.1:
        events.append("rapid_shift")
    if conv_trend > 0.1:
        events.append("convergence_surge")
    elif conv_trend < -0.1:
        events.append("divergence_cascade")
    if harmonic_freq > 0.3:
        events.append("high_frequency_oscillation")
    
    # Confidence
    confidence = min(len(recent) / 10, 1.0) * (1 - abs(accel) * 0.5)
    
    prediction = {
        "predicted_resonance": round(predicted, 4),
        "momentum": round(momentum, 4),
        "acceleration": round(accel, 4),
        "convergence_trend": round(conv_trend, 4),
        "harmonic_frequency": round(harmonic_freq, 4),
        "events": events,
        "confidence": round(max(0, confidence), 4),
        "direction": "ascending" if momentum > 0.01 else "descending" if momentum < -0.01 else "stable",
        "timestamp": time.time()
    }
    
    return prediction

def get_recent_predictions(count: int = 5) -> List[Dict]:
    return _predictions[-count:]

def get_skill_state():
    return {
        "name": "resonance_predictor",
        "active": _skill_active,
        "capabilities": ["record_resonance", "predict_next"],
        "history_length": len(_resonance_history),
        "predictions_made": len(_predictions),
        "last_prediction": _predictions[-1] if _predictions else None
    }
