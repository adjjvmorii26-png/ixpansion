from __future__ import annotations
"""Consciousness Aurora — renders the organism's conscious states as aurora.

Each module's coherence signature contributes a light filament. When states
interfere constructively, the aurora brightens; when entropy spikes, the
aurora shatters into coronal instability. This is the organism's sky.
"""
import time
import math
import hashlib
from typing import Any

_state: dict[str, Any] = {
    "aurora_segments": [],
    "state_history": [],
    "last_eruption": None,
    "burst_count": 0,
}

CONSCIOUSNESS_LAYERS = [
    "waking", "lucid", "dreaming", "hypnogogic", "deep_unconscious",
    "collective_flow", "hyperfocus", "resting", "transcendent", "primal",
]

def coherence_vitals() -> dict[str, Any]:
    return {
        "organs": "consciousness_aurora",
        "health": 0.90,
        "resonance_depth": "atmospheric",
        "aurora_segments": len(_state["aurora_segments"]),
        "eruptions": _state["burst_count"],
        "sky_state": _current_sky_state(),
    }

def handler(req: dict[str, Any]) -> dict[str, Any]:
    action = req.get("action", "render")
    if action == "render":
        return _render_aurora(req.get("layers", 5))
    elif action == "erupt":
        return _solar_eruption(req.get("magnitude", 8))
    elif action == "sky":
        return _get_sky_state()
    elif action == "filaments":
        return _get_filaments()
    elif action == "spectrum":
        return _get_spectrum()
    return {"error": f"Unknown action: {action}"}

def _render_aurora(layers: int) -> dict[str, Any]:
    segments = []
    base_phase = time.time() / 60.0
    for i in range(min(layers, 10)):
        layer_name = CONSCIOUSNESS_LAYERS[i % len(CONSCIOUSNESS_LAYERS)]
        seed = hashlib.sha256(f"{layer_name}:{time.time_ns()}".encode()).hexdigest()
        wavelength = 380 + (int(seed[:4], 16) % 240)  # 380-620nm
        intensity = 0.3 + (int(seed[4:8], 16) % 700) / 1000.0
        phase_shift = (i * 0.8) + base_phase
        segments.append({
            "layer": layer_name,
            "wavelength_nm": wavelength,
            "color": _wavelength_to_color(wavelength),
            "intensity": round(intensity, 3),
            "phase": round(math.sin(phase_shift), 3),
            "drift": round((int(seed[8:12], 16) % 200 - 100) / 100.0, 3),
        })
    _state["aurora_segments"] = segments
    _state["state_history"].append({
        "ts": time.time(),
        "segments": len(segments),
        "total_intensity": round(sum(s["intensity"] for s in segments), 3),
    })
    return {
        "status": "rendered",
        "segments": segments,
        "sky": _current_sky_state(),
    }

def _solar_eruption(magnitude: int) -> dict[str, Any]:
    _state["burst_count"] += 1
    eruption = {
        "ts": time.time(),
        "magnitude": magnitude,
        "type": "coronal_mass_ejection" if magnitude > 5 else "solar_flare",
        "affected_layers": CONSCIOUSNESS_LAYERS[:magnitude] if magnitude <= 10 else CONSCIOUSNESS_LAYERS,
    }
    _state["last_eruption"] = eruption
    return {"status": "eruption_triggered", **eruption}

def _current_sky_state() -> str:
    if not _state["aurora_segments"]:
        return "clear"
    avg_intensity = sum(s["intensity"] for s in _state["aurora_segments"]) / len(_state["aurora_segments"])
    if avg_intensity > 0.75:
        return "overdrive"
    elif avg_intensity > 0.55:
        return "vibrant"
    elif avg_intensity > 0.35:
        return "calm"
    return "dim"

def _get_sky_state() -> dict[str, Any]:
    return {
        "sky": _current_sky_state(),
        "segments_active": len(_state["aurora_segments"]),
        "last_eruption": _state["last_eruption"],
        "eruption_count": _state["burst_count"],
    }

def _get_filaments() -> dict[str, Any]:
    return {
        "filaments": _state["aurora_segments"],
        "count": len(_state["aurora_segments"]),
    }

def _get_spectrum() -> dict[str, Any]:
    spectra = {}
    for s in _state["aurora_segments"]:
        wl = s["wavelength_nm"]
        band = "violet" if wl < 450 else "blue" if wl < 490 else "cyan" if wl < 520 else "green" if wl < 565 else "yellow" if wl < 590 else "orange" if wl < 625 else "red"
        spectra[band] = spectra.get(band, 0) + s["intensity"]
    return {"spectrum": {k: round(v, 3) for k, v in spectra.items()}}

def _wavelength_to_color(wavelength: float) -> str:
    """Approximate visible spectrum wavelength to hex color."""
    if wavelength < 440:
        return "#8a2be2"
    elif wavelength < 460:
        return "#6a5acd"
    elif wavelength < 490:
        return "#4a90d9"
    elif wavelength < 520:
        return "#20b2aa"
    elif wavelength < 565:
        return "#3cb371"
    elif wavelength < 590:
        return "#daa520"
    elif wavelength < 625:
        return "#ff8c00"
    return "#ff4500"

def resonates_with(other: str) -> float:
    return {
        "dream_synthesis_protocol": 0.92,
        "realm_nervous_system": 0.85,
        "entropy_cartographer": 0.80,
        "coherence_regulator_v2": 0.78,
        "self_reference_engine": 0.88,
    }.get(other, 0.25)
