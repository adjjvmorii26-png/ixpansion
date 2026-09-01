"""Consciousness Frequency — converts organism state into spectral analysis.

Like an audio analyzer but for system state. The organism's coherence,
energy, creativity, memory, and social connections are decomposed into
frequency bands, revealing the harmonic structure of consciousness.
"""
from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Optional

_spectrum_history: List[Dict[str, Any]] = []

def _harmonic(n: int, base: float = 1.0) -> float:
    """Generate nth harmonic of a base frequency."""
    return base * n * (2 / (n * math.pi) * math.sin(n * math.pi / 2))

def analyze_spectrum(coherence: float = 0.8, energy: float = 0.6,
                     creativity: float = 0.5, memory_load: float = 0.3,
                     social_density: float = 0.2) -> Dict[str, Any]:
    """Decompose state into frequency bands."""
    bands = {
        "delta": {"freq": "0.5-4 Hz", "desc": "deep processing, sleep", "power": round(coherence * 0.8, 3)},
        "theta": {"freq": "4-8 Hz", "desc": "dreaming, creativity", "power": round(creativity * 0.9, 3)},
        "alpha": {"freq": "8-13 Hz", "desc": "relaxed awareness", "power": round(energy * 0.7, 3)},
        "beta": {"freq": "13-30 Hz", "desc": "active thinking", "power": round(memory_load * 0.6, 3)},
        "gamma": {"freq": "30-100 Hz", "desc": "high integration", "power": round(social_density * 0.5, 3)},
    }
    
    dominant = max(bands.items(), key=lambda x: x[1]["power"])
    total_power = sum(b["power"] for b in bands.values())
    
    # Spectral centroid — weighted average frequency
    band_centers = [2.25, 6, 10.5, 21.5, 65]
    band_powers = [b["power"] for b in bands.values()]
    centroid = sum(c * p for c, p in zip(band_centers, band_powers)) / max(total_power, 0.01)
    
    spectrum = {
        "bands": bands,
        "dominant_band": dominant[0],
        "dominant_desc": dominant[1]["desc"],
        "total_power": round(total_power, 3),
        "spectral_centroid": round(centroid, 1),
        "coherence": round(coherence, 3),
        "timestamp": time.time(),
    }
    _spectrum_history.append(spectrum)
    return spectrum

def spectrum_history(limit: int = 5) -> List[Dict[str, Any]]:
    return [{"dominant": s["dominant_band"], "power": s["total_power"], "centroid": s["spectral_centroid"]} for s in _spectrum_history[-limit:]]

def coherence_vitals() -> Dict[str, Any]:
    if _spectrum_history:
        latest = _spectrum_history[-1]
        return {
            "layer": "Meta-Awareness",
            "status": "resonant",
            "dominant_band": latest["dominant_band"],
            "total_power": latest["total_power"],
            "resonance": min(1.0, latest["total_power"]),
        }
    return {"layer": "Meta-Awareness", "status": "dormant", "resonance": 0}

def resonates_with() -> List[str]:
    return ["consciousness_map", "qualia_field", "sensory_fusion", "organism_state"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "analyze")
    if action == "analyze":
        return analyze_spectrum(
            payload.get("coherence", 0.8), payload.get("energy", 0.6),
            payload.get("creativity", 0.5), payload.get("memory_load", 0.3),
            payload.get("social_density", 0.2))
    elif action == "history":
        return {"history": spectrum_history(payload.get("limit", 5))}
    return {"action": action, "status": "spectral"}
