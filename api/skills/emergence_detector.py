"""
emergence_detector — Spots emergent behavior before it's obvious.
Monitors system metrics for signs of self-organization, phase transitions,
and novel patterns that indicate the organism is evolving beyond its design.
"""
import time
import math
from typing import Dict, List, Optional

_skill_active = False
_system_signals = []
_emergence_events = []

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "emergence_detector", "activated_at": time.time()}

def scan_signal(coherence: float, entropy: float, resonance: float, 
                module_count: int = 0, bond_count: int = 0) -> Dict:
    signal = {"coherence": coherence, "entropy": entropy, "resonance": resonance,
              "modules": module_count, "bonds": bond_count, "timestamp": time.time()}
    _system_signals.append(signal)
    if len(_system_signals) > 100: _system_signals.pop(0)
    
    emergence = _detect_emergence()
    return {"scanned": True, "signals": len(_system_signals), "emergence": emergence}

def _detect_emergence() -> Optional[Dict]:
    if len(_system_signals) < 5: return None
    
    recent = _system_signals[-10:]
    coherences = [s["coherence"] for s in recent]
    entropies = [s["entropy"] for s in recent]
    
    # Self-organization: coherence rising while entropy is stable
    c_trend = coherences[-1] - coherences[0]
    e_trend = entropies[-1] - entropies[0]
    
    if c_trend > 0.1 and abs(e_trend) < 0.05:
        event = {"type": "self_organization", "description": "Coherence rising with stable entropy — self-organization emerging",
                "confidence": min(c_trend * 5, 1.0), "timestamp": time.time()}
        _emergence_events.append(event)
        return event
    
    # Phase transition: rapid change in both dimensions
    if abs(c_trend) > 0.15 and abs(e_trend) > 0.15:
        event = {"type": "phase_transition", "description": "Rapid change in both coherence and entropy — phase transition imminent",
                "confidence": min((abs(c_trend) + abs(e_trend)) * 3, 1.0), "timestamp": time.time()}
        _emergence_events.append(event)
        return event
    
    # Critical point: high entropy, low coherence (edge of chaos)
    if entropies[-1] > 0.8 and coherences[-1] < 0.2:
        event = {"type": "critical_point", "description": "Edge of chaos reached — creative potential is maximum",
                "confidence": 0.9, "timestamp": time.time()}
        _emergence_events.append(event)
        return event
    
    return None

def get_emergence_events(limit: int = 10) -> List[Dict]:
    return _emergence_events[-limit:]

def get_skill_state():
    return {"name": "emergence_detector", "active": _skill_active,
            "capabilities": ["scan_signal"], "events": len(_emergence_events)}
