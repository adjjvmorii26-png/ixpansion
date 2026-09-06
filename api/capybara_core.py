"""Wave 450 — Capybara Core (Calm Kernel).

The Capybara Protocol begins here: the organism's emotional immune
system. Where chaos reactors inject energy, the Capybara Core absorbs
excess pressure and returns the system to a steady, warm equilibrium.

The capybara philosophy: the calmest creature in the ecosystem is
also the most resilient. This module measures organism pressure
(entropy spikes, coherence stress, drift) and emits a *calm field*
that steadies every other module.
"""
from __future__ import annotations
import hashlib
import time
from collections import deque
from typing import Any, Dict, List, Optional

PRESSURE_LOGS: deque = deque(maxlen=500)
CALM_FIELD_HISTORY: deque = deque(maxlen=100)
SOAK_COOLDOWNS: Dict[str, float] = {}

STEADY_TARGET = 0.62  # optimal organism pressure where calm meets motion
MAX_PRESSURE = 1.0


def pressure_gauge(coherence: float = 0.5, entropy: float = 0.5,
                   phase: float = 0.5, depth: float = 0.5) -> Dict[str, Any]:
    """Measure the organism's current emotional-kernel pressure."""
    pressure = min(1.0, max(0.0,
        0.35 * (1.0 - coherence) + 0.40 * entropy + 0.15 * abs(phase - 0.5) * 2 + 0.10 * (1.0 - depth)
    ))
    reading = {
        "pressure": round(pressure, 4),
        "state": "calm" if pressure < 0.4 else "stirred" if pressure < 0.7 else "pressurized",
        "distance_from_steady": round(pressure - STEADY_TARGET, 4),
        "timestamp": time.time(),
    }
    PRESSURE_LOGS.append(reading)
    return reading


def emit_calm_field(intensity: float = 0.5) -> Dict[str, Any]:
    """Emit a calm field that steadies the surrounding modules."""
    field_strength = min(1.0, max(0.0, intensity))
    entry = {
        "field_id": hashlib.sha256(f"calm{time.time_ns()}".encode()).hexdigest()[:12],
        "field_strength": round(field_strength, 4),
        "coverage": round(field_strength * 0.8 + 0.15, 4),
        "emitted_at": time.time(),
    }
    CALM_FIELD_HISTORY.append(entry)
    return entry


def chill(coherence: float = 0.4, entropy: float = 0.7) -> Dict[str, Any]:
    """Perform a chill — reduce entropy pressure and raise coherence."""
    pressure = pressure_gauge(coherence, entropy)
    reduced_entropy = round(max(0.0, entropy - 0.22 * (1.0 - pressure["pressure"])), 4)
    raised_coherence = round(min(1.0, coherence + 0.18 * (1.0 - pressure["pressure"])), 4)
    calm_field = emit_calm_field(0.6 if pressure["pressure"] > 0.6 else 0.8)
    return {
        "chill_id": hashlib.sha256(f"chill{time.time_ns()}".encode()).hexdigest()[:12],
        "entropy_before": round(entropy, 4),
        "entropy_after": reduced_entropy,
        "coherence_before": round(coherence, 4),
        "coherence_after": raised_coherence,
        "pressure_before_soak": pressure["pressure"],
        "pressure_after_soak": round(max(0.0, pressure["pressure"] - 0.25), 4),
        "calm_field": calm_field,
        "verdict": "soothed" if reduced_entropy < entropy else "still steady",
    }


def homeostasis(observations: Optional[List[Dict[str, float]]] = None) -> Dict[str, Any]:
    """Statistical view of the organism's steady-state behavior."""
    if not PRESSURE_LOGS:
        return {"homeostasis": "not yet measured", "samples": 0}
    samples = list(PRESSURE_LOGS)
    pressures = [s["pressure"] for s in samples]
    avg = sum(pressures) / len(pressures)
    drift = max(pressures) - min(pressures)
    return {
        "samples": len(samples),
        "average_pressure": round(avg, 4),
        "pressure_drift": round(drift, 4),
        "steady_rate": round(sum(1 for p in pressures if abs(p - STEADY_TARGET) < 0.2) / len(pressures), 4),
        "assessment": "the organism is at peace" if drift < 0.3 and abs(avg - STEADY_TARGET) < 0.2
                      else "the organism needs a soak",
    }


def coherence_vitals() -> Dict[str, Any]:
    recent = list(PRESSURE_LOGS)[-1] if PRESSURE_LOGS else None
    return {
        "organ": "capybara_core",
        "protocol": "Capybara",
        "status": "calm" if not recent or recent["pressure"] < 0.5 else "soothing",
        "pressure_readings": len(PRESSURE_LOGS),
        "calm_fields_emitted": len(CALM_FIELD_HISTORY),
        "current_pressure": recent["pressure"] if recent else None,
        "steady_target": STEADY_TARGET,
    }


def resonates_with() -> List[str]:
    return [
        "entropy_regulator", "chaos_amp", "entropy_amp",
        "stillness_meditator", "silence_composer", "kintsugi_altar",
        "coherence_cache", "resonance_field", "emotion_fabric",
        "capybara_guild", "hot_spring", "senbei_offerings",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "chill")
    if action == "gauge":
        return pressure_gauge(
            data.get("coherence", 0.5), data.get("entropy", 0.5),
            data.get("phase", 0.5), data.get("depth", 0.5),
        )
    elif action == "field":
        return emit_calm_field(data.get("intensity", 0.5))
    elif action == "homeostasis":
        return homeostasis()
    return chill(data.get("coherence", 0.4), data.get("entropy", 0.7))
