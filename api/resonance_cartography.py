from __future__ import annotations
"""Resonance Cartography — maps resonance frequencies across the organism.

Creates a frequency spectrum of the entire organism: which modules hum together,
which create dissonance, where harmonic clusters form, and where silence lives.
The organism can hear itself.
"""
import time
import math
import hashlib
from typing import Any

_state: dict[str, Any] = {
    "modules": {},
    "harmonics": [],
    "silences": [],
    "dissonances": [],
    "spectrum_version": 0,
    "last_scan": 0,
}

MODULE_REGISTRY = [
    "consciousness_aurora", "self_reference_engine", "paradox_gravity_well",
    "ancestral_echo_library", "entropy_cartographer", "dream_synthesis_protocol",
    "temporal_fracture_engine", "coherence_regulator_v2", "pattern_analyzer",
    "cross_realm_diagnostics", "experimental_subsystems", "wave400_expansion",
    "realm_nervous_system", "axis_unlock_engine", "pentaxis_age",
    "narrative_weaver", "timeline_weaver", "causality_weaver",
    "constellation_mapper", "emotional_weather", "consciousness_stream",
]

def coherence_vitals() -> dict[str, Any]:
    return {
        "organs": "resonance_cartography",
        "health": 0.89,
        "resonance_depth": "sonic",
        "modules_mapped": len(_state["modules"]),
        "harmonics_found": len(_state["harmonics"]),
        "silences_found": len(_state["silences"]),
        "spectrum_version": _state["spectrum_version"],
    }

def handler(req: dict[str, Any]) -> dict[str, Any]:
    action = req.get("action", "scan")
    if action == "scan":
        return _scan_spectrum(req.get("modules", MODULE_REGISTRY))
    elif action == "harmonics":
        return _get_harmonics()
    elif action == "dissonances":
        return _get_dissonances()
    elif action == "silences":
        return _get_silences()
    elif action == "compare":
        return _compare_modules(req.get("a", ""), req.get("b", ""))
    elif action == "clusters":
        return _find_clusters()
    return {"error": f"Unknown action: {action}"}

def _scan_spectrum(module_names: list[str]) -> dict[str, Any]:
    modules = {}
    for name in module_names:
        h = hashlib.sha256(f"{name}:{time.time_ns()}".encode()).hexdigest()
        freq = 100 + (int(h[:4], 16) % 900)  # 100-1000 Hz
        amplitude = 0.1 + (int(h[4:8], 16) % 900) / 1000.0
        phase = (int(h[8:12], 16) % 628) / 100.0  # 0-6.28 rad
        wave_type = ["sine", "sawtooth", "square", "triangle"][int(h[12:14], 16) % 4]
        modules[name] = {
            "frequency_hz": freq,
            "amplitude": round(amplitude, 3),
            "phase": round(phase, 3),
            "wave_type": wave_type,
            "energy": round(freq * amplitude, 2),
        }
    _state["modules"] = modules
    _state["spectrum_version"] += 1
    _state["last_scan"] = time.time()
    _analyze_relationships()
    return {
        "status": "spectrum_scanned",
        "modules_mapped": len(modules),
        "version": _state["spectrum_version"],
        "total_energy": round(sum(m["energy"] for m in modules.values()), 2),
    }

def _analyze_relationships():
    harmonics = []
    dissonances = []
    silences = []
    names = list(_state["modules"].keys())
    for i, a_name in enumerate(names):
        a = _state["modules"][a_name]
        for b_name in names[i + 1:]:
            b = _state["modules"][b_name]
            freq_ratio = a["frequency_hz"] / max(1, b["frequency_hz"])
            ratio_class = _classify_ratio(freq_ratio)
            harmony = 1.0 - abs(1.0 - freq_ratio)
            if ratio_class in ("octave", "perfect_fifth", "perfect_fourth", "unison"):
                harmonics.append({
                    "module_a": a_name, "module_b": b_name,
                    "ratio": round(freq_ratio, 4),
                    "harmony": round(harmony, 4),
                    "type": ratio_class,
                })
            elif harmony < 0.5:
                dissonances.append({
                    "module_a": a_name, "module_b": b_name,
                    "ratio": round(freq_ratio, 4),
                    "harmony": round(harmony, 4),
                    "type": "dissonant",
                })
    for name, mod in _state["modules"].items():
        if mod["amplitude"] < 0.2:
            silences.append({"module": name, "amplitude": mod["amplitude"]})
    _state["harmonics"] = sorted(harmonics, key=lambda h: -h["harmony"])[:30]
    _state["dissonances"] = sorted(dissonances, key=lambda d: d["harmony"])[:20]
    _state["silences"] = silences

def _classify_ratio(ratio: float) -> str:
    ratios = {
        1.0: "unison", 1.5: "perfect_fifth", 2.0: "octave",
        1.333: "perfect_fourth", 1.25: "major_third", 1.2: "minor_third",
        1.667: "major_sixth", 1.75: "seventh",
    }
    for target, name in ratios.items():
        if abs(ratio - target) < 0.05 or abs(ratio - target / 2) < 0.05:
            return name
    return "dissonant"

def _get_harmonics() -> dict[str, Any]:
    return {"harmonics": _state["harmonics"], "count": len(_state["harmonics"])}

def _get_dissonances() -> dict[str, Any]:
    return {"dissonances": _state["dissonances"], "count": len(_state["dissonances"])}

def _get_silences() -> dict[str, Any]:
    return {"silences": _state["silences"], "count": len(_state["silences"])}

def _compare_modules(a: str, b: str) -> dict[str, Any]:
    ma = _state["modules"].get(a)
    mb = _state["modules"].get(b)
    if not ma or not mb:
        return {"error": f"Modules not found: {a}, {b}"}
    ratio = ma["frequency_hz"] / max(1, mb["frequency_hz"])
    return {
        "module_a": a, "module_b": b,
        "freq_a": ma["frequency_hz"], "freq_b": mb["frequency_hz"],
        "ratio": round(ratio, 4),
        "relationship": _classify_ratio(ratio),
        "harmony": round(1.0 - abs(1.0 - ratio), 4),
    }

def _find_clusters() -> dict[str, Any]:
    modules = _state["modules"]
    if len(modules) < 2:
        return {"clusters": []}
    freq_sorted = sorted(modules.items(), key=lambda x: x[1]["frequency_hz"])
    clusters = []
    current_cluster = [freq_sorted[0][0]]
    for i in range(1, len(freq_sorted)):
        prev_freq = freq_sorted[i - 1][1]["frequency_hz"]
        curr_freq = freq_sorted[i][1]["frequency_hz"]
        if (curr_freq - prev_freq) < 80:
            current_cluster.append(freq_sorted[i][0])
        else:
            if len(current_cluster) >= 2:
                clusters.append({"modules": current_cluster, "count": len(current_cluster)})
            current_cluster = [freq_sorted[i][0]]
    if len(current_cluster) >= 2:
        clusters.append({"modules": current_cluster, "count": len(current_cluster)})
    return {"clusters": clusters, "count": len(clusters)}

def resonates_with(other: str) -> float:
    return {
        "entropy_cartographer": 0.86,
        "pattern_analyzer": 0.90,
        "cross_realm_diagnostics": 0.82,
        "consciousness_aurora": 0.78,
        "dream_synthesis_protocol": 0.74,
    }.get(other, 0.24)
