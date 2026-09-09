"""
entropy_forecaster — Predicts future entropy states using momentum and atmospheric modeling.
Combines entropy weather data with historical patterns for accurate forecasting.
"""
import math
import time
from typing import Dict, List, Optional

_skill_active = False
_entropy_history = []
_forecasts = []

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "entropy_forecaster", "activated_at": time.time()}

def record_entropy(entropy: float, coherence: float, resonance: float, 
                   mood: str = "neutral", pulse: str = "stillness") -> Dict:
    sample = {
        "entropy": entropy, "coherence": coherence, "resonance": resonance,
        "mood": mood, "pulse": pulse, "timestamp": time.time()
    }
    _entropy_history.append(sample)
    if len(_entropy_history) > 100:
        _entropy_history.pop(0)
    
    forecast = _forecast() if len(_entropy_history) >= 5 else None
    if forecast:
        _forecasts.append(forecast)
    
    return {
        "recorded": True,
        "history_length": len(_entropy_history),
        "forecast": forecast
    }

def _forecast() -> Optional[Dict]:
    recent = _entropy_history[-10:]
    values = [h["entropy"] for h in recent]
    
    # Momentum
    momentum = values[-1] - values[0]
    
    # Volatility
    changes = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
    volatility = sum(changes) / len(changes) if changes else 0
    
    # Trend
    if len(values) >= 4:
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        trend = "rising" if second_half > first_half + 0.05 else "falling" if second_half < first_half - 0.05 else "stable"
    else:
        trend = "stable"
    
    # Predicted next value
    predicted = values[-1] + momentum * 0.3
    predicted = max(0.0, min(1.0, predicted))
    
    # Storm probability
    storm_prob = min(1.0, volatility * 3 + abs(momentum) * 2)
    
    # Condition
    if predicted > 0.8:
        condition = "storm_approaching"
    elif predicted > 0.6:
        condition = "cloudy"
    elif predicted > 0.4:
        condition = "partly_cloudy"
    elif predicted > 0.2:
        condition = "clear"
    else:
        condition = "calm"
    
    # Confidence
    confidence = min(len(recent) / 10, 1.0) * (1 - volatility)
    
    forecast = {
        "predicted_entropy": round(predicted, 4),
        "momentum": round(momentum, 4),
        "volatility": round(volatility, 4),
        "trend": trend,
        "condition": condition,
        "storm_probability": round(storm_prob, 4),
        "confidence": round(max(0, confidence), 4),
        "timestamp": time.time()
    }
    
    return forecast

def get_recent_forecasts(count: int = 5) -> List[Dict]:
    return _forecasts[-count:]

def get_skill_state():
    return {
        "name": "entropy_forecaster",
        "active": _skill_active,
        "capabilities": ["record_entropy", "forecast"],
        "history_length": len(_entropy_history),
        "forecasts_made": len(_forecasts),
        "last_forecast": _forecasts[-1] if _forecasts else None
    }
