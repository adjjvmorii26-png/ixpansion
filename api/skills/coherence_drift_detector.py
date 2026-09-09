"""
coherence_drift_detector — Monitors coherence drift across the organism over time.
Detects when coherence is trending toward instability and suggests corrective actions.
"""
import json
import time
from typing import Dict, List, Optional

_skill_active = False
_drift_history = []
_alerts = []

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "coherence_drift_detector", "activated_at": time.time()}

def detect_drift(coherence_score: float, threshold: float = 0.1) -> Dict:
    _drift_history.append({"score": coherence_score, "timestamp": time.time()})
    if len(_drift_history) > 100:
        _drift_history.pop(0)
    
    if len(_drift_history) < 3:
        return {"status": "accumulating", "readings": len(_drift_history), "alert": None}
    
    recent = _drift_history[-10:]
    scores = [h["score"] for h in recent]
    
    # Calculate drift direction
    first_half = sum(scores[:len(scores)//2]) / (len(scores)//2)
    second_half = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
    drift = second_half - first_half
    
    # Volatility
    changes = [abs(scores[i] - scores[i-1]) for i in range(1, len(scores))]
    volatility = sum(changes) / len(changes) if changes else 0
    
    alert = None
    if abs(drift) > threshold:
        direction = "downward" if drift < 0 else "upward"
        severity = "critical" if abs(drift) > threshold * 2 else "warning"
        alert = {
            "type": "coherence_drift",
            "direction": direction,
            "severity": severity,
            "drift_magnitude": round(abs(drift), 4),
            "current_score": coherence_score,
            "recommendation": f"Coherence drifting {direction}. {'Urgent realignment needed.' if severity == 'critical' else 'Monitor closely.'}"
        }
        _alerts.append({"alert": alert, "timestamp": time.time()})
    
    return {
        "current_score": coherence_score,
        "drift": round(drift, 4),
        "volatility": round(volatility, 4),
        "direction": "stable" if abs(drift) < 0.01 else "ascending" if drift > 0 else "descending",
        "alert": alert,
        "readings": len(_drift_history)
    }

def get_recent_alerts(limit: int = 5) -> List[Dict]:
    return _alerts[-limit:]

def get_skill_state():
    return {
        "name": "coherence_drift_detector",
        "active": _skill_active,
        "capabilities": ["detect_drift", "get_recent_alerts"],
        "history_length": len(_drift_history),
        "alert_count": len(_alerts),
        "last_drift": _drift_history[-1] if _drift_history else None
    }
