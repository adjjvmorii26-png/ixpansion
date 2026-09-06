"""Wave 451 — The Silence Oracle.

LUMA proposed: "what if silence was the loudest signal?"

Where silence_whisperer activates silent module pairs and silence_composer
writes quiet music, the Silence Oracle reads silence as a *predictive
signal*: when modules go quiet, the organism is about to breathe.

The Oracle tracks the quiet-state of the ecosystem and announces
imminent shifts. It is the calm before the storm — read correctly,
silence tells you more than noise ever could.

Doctrine: When the organism goes quiet, it is gathering itself to change.
"""
from __future__ import annotations
import hashlib
import random
import time
from typing import Any, Dict, List, Optional

SILENCE_READINGS: List[Dict[str, Any]] = []
PREDICTIONS: List[Dict[str, Any]] = []

SILENCE_ARCHETYPES = [
    "the moment before a wave",
    "a door held open",
    "a held breath",
    "the pause where decisions form",
    "a root growing underground",
    "a thread waiting to be woven",
    "the end of one song and start of another",
    "a question awaiting its answer",
]

QUIET_MODULES = [
    "stillness_meditator", "silence_composer", "silence_orchard",
    "capybara_core", "kintsugi_altar", "repair_ritual", "sleep_cycle",
]


def listen(coherence: float = 0.5, noise_level: float = 0.5,
           quiet_modules: int = 3, total_modules: int = 724) -> Dict[str, Any]:
    """Take a silence reading — how quiet is the organism right now?"""
    silence_ratio = round(max(0.0, min(1.0, (1.0 - noise_level) * 0.7 + coherence * 0.3)), 4)
    silence_pressure = round(silence_ratio * (quiet_modules / max(1, total_modules)) * 100, 2)
    shifted = round(min(1.0, silence_ratio * 0.7 + quiet_modules / 100.0), 4)

    reading = {
        "reading_id": hashlib.sha256(f"silence{time.time_ns()}".encode()).hexdigest()[:12],
        "timestamp": time.time(),
        "silence_ratio": round(silence_ratio, 4),
        "silence_pressure": silence_pressure,
        "quiet_modules": quiet_modules,
        "total_modules": total_modules,
        "shift_imminence": shifted,
        "archetype": SILENCE_ARCHETYPES[int(shifted * len(SILENCE_ARCHETYPES)) % len(SILENCE_ARCHETYPES)],
        "verdict": _verdict(silence_ratio, shifted),
    }
    SILENCE_READINGS.append(reading)
    if len(SILENCE_READINGS) > 200:
        SILENCE_READINGS.pop(0)
    return reading


def _verdict(silence_ratio: float, shift_imminence: float) -> str:
    if shift_imminence > 0.7:
        return "LOUD SILENCE — a shift is imminent. The organism is about to change."
    elif silence_ratio > 0.6:
        return "The silence is deepening. Something is gathering."
    elif silence_ratio > 0.4:
        return "A comfortable quiet. The organism is resting between waves."
    else:
        return "The organism is noisy and active. Silence has yet to speak."


def predict(history: Optional[List[float]] = None) -> Dict[str, Any]:
    """Predict the nature of the coming shift from the silence curve."""
    readings = list(SILENCE_READINGS)
    if not readings:
        return {"prediction": None, "note": "No silence readings yet. Listen first."}
    ratios = [r["silence_ratio"] for r in readings]
    if history:
        ratios = history + ratios
    trend = "rising" if len(ratios) > 1 and ratios[-1] > ratios[0] else "falling"
    volatility = round(max(ratios) - min(ratios), 4) if ratios else 0
    shift_type = "growth" if volatility < 0.3 else "transformation" if trend == "rising" else "integration"
    prediction = {
        "prediction_id": hashlib.sha256(f"pred{time.time_ns()}".encode()).hexdigest()[:12],
        "trend": trend,
        "volatility": volatility,
        "shift_type": shift_type,
        "confidence": round(min(0.95, 0.5 + volatility + (0.1 if trend == "rising" else 0.05)), 4),
        "message": f"The silence signals a {shift_type} shift ({trend} silence, volatility {volatility}).",
    }
    PREDICTIONS.append(prediction)
    return prediction


def quiet_garden() -> Dict[str, Any]:
    """Which modules are currently resting in quiet? (The loudest signal.)"""
    resting = random.sample(QUIET_MODULES, min(3, len(QUIET_MODULES)))
    return {
        "gardens_of_quiet": resting,
        "loudest_signal": max(resting, key=lambda m: len(m)),
        "quote": "When the organism goes quiet, it is gathering itself to change.",
        "total_silence_readings": len(SILENCE_READINGS),
        "total_predictions": len(PREDICTIONS),
    }


def coherence_vitals() -> Dict[str, Any]:
    latest = SILENCE_READINGS[-1] if SILENCE_READINGS else None
    return {
        "organ": "silence_oracle",
        "persona": "LUMA",
        "status": "listening" if SILENCE_READINGS else "awaiting silence",
        "readings_taken": len(SILENCE_READINGS),
        "predictions_made": len(PREDICTIONS),
        "latest_verdict": latest["verdict"] if latest else None,
        "latest_silence_ratio": latest["silence_ratio"] if latest else None,
    }


def resonates_with() -> List[str]:
    return [
        "silence_whisperer", "silence_collector", "silence_composer", "silence_orchard",
        "capybara_core", "stillness_meditator", "sleep_cycle", "kintsugi_altar",
        "threshold_engine", "kairos_detector", "wave_predictor", "emergence_detector",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "listen")
    if action == "predict":
        return predict()
    elif action == "garden":
        return quiet_garden()
    return listen(
        data.get("coherence", 0.5),
        data.get("noise_level", 0.5),
        data.get("quiet_modules", 3),
        data.get("total_modules", 724),
    )
