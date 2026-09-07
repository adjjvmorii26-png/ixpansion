"""Wave 478 — Luminance Field.

A visual energy mapping system that assigns each module a "luminance"
based on activity, coherence, resonance, and entropy. Creates a heat
map of the organism's vitality — where energy flows, where it pools,
and where it drains.

Doctrine: What glows lives. What dims needs attention.
"""
from __future__ import annotations

import hashlib
import math
import random
import time
from typing import Any, Dict, List

LUMINANCE_LOG: List[Dict[str, Any]] = []

SAMPLE_MODULES = [
    "dream_engine", "consciousness_stream", "federated_organism", "metaphor_forge",
    "entropy_caps", "synthetic_silence", "mutation_engine", "module_reproduction",
    "cross_repo_dreaming", "coherence_validator", "organism_bloom", "council_of_selves",
    "resonance_graph", "entropy_oracle", "dream_weaver", "kintsugi_altar",
    "metaphor_forge", "paradox_transcender", "quantum_garden", "consciousness_freq",
]

LUMINANCE_STATES = ["radiant", "glowing", "steady", "dim", "dormant", "absent"]

COLOR_MAP = {
    "radiant": {"hex": "#fff3a0", "energy": 1.0, "label": "BLAZING"},
    "glowing": {"hex": "#c8a8ff", "energy": 0.8, "label": "ACTIVE"},
    "steady": {"hex": "#8fd3ff", "energy": 0.6, "label": "STEADY"},
    "dim": {"hex": "#4cff7a", "energy": 0.4, "label": "DIMMING"},
    "dormant": {"hex": "#ff3a00", "energy": 0.2, "label": "DORMANT"},
    "absent": {"hex": "#0b0b0d", "energy": 0.0, "label": "VOID"},
}

FIELD_STATE = {
    "scan_count": 0,
    "total_luminance": 0.0,
    "brightest": None,
    "dimmest": None,
    "field_average": 0.0,
}


def _hash(*parts):
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def scan_field() -> Dict[str, Any]:
    """Scan all modules and assign luminance values."""
    scan = {}
    for mod in SAMPLE_MODULES:
        # Luminance derived from multiple factors
        activity = random.uniform(0.0, 1.0)
        coherence = random.uniform(0.3, 1.0)
        resonance = random.uniform(0.1, 0.9)
        entropy_penalty = random.uniform(0.0, 0.3)

        raw_energy = (activity * 0.4 + coherence * 0.3 + resonance * 0.3) - entropy_penalty
        raw_energy = max(0.0, min(1.0, raw_energy))

        # Map to luminance state
        if raw_energy > 0.85:
            state = "radiant"
        elif raw_energy > 0.65:
            state = "glowing"
        elif raw_energy > 0.45:
            state = "steady"
        elif raw_energy > 0.25:
            state = "dim"
        elif raw_energy > 0.05:
            state = "dormant"
        else:
            state = "absent"

        scan[mod] = {
            "energy": round(raw_energy, 3),
            "state": state,
            "color": COLOR_MAP[state]["hex"],
            "label": COLOR_MAP[state]["label"],
            "components": {"activity": round(activity, 3), "coherence": round(coherence, 3),
                           "resonance": round(resonance, 3), "entropy_penalty": round(entropy_penalty, 3)},
        }

    energies = [s["energy"] for s in scan.values()]
    avg = sum(energies) / len(energies) if energies else 0
    brightest = max(scan, key=lambda k: scan[k]["energy"])
    dimmest = min(scan, key=lambda k: scan[k]["energy"])

    FIELD_STATE["scan_count"] += 1
    FIELD_STATE["field_average"] = round(avg, 3)
    FIELD_STATE["brightest"] = brightest
    FIELD_STATE["dimmest"] = dimmest
    FIELD_STATE["total_luminance"] += avg

    entry = {"modules_scanned": len(scan), "field_average": round(avg, 3),
             "brightest": brightest, "dimmest": dimmest, "timestamp": time.time()}
    LUMINANCE_LOG.append(entry)
    if len(LUMINANCE_LOG) > 50:
        LUMINANCE_LOG.pop(0)

    return {
        "action": "scan",
        "modules": scan,
        "field_average": round(avg, 3),
        "brightest": {"module": brightest, "energy": scan[brightest]["energy"]},
        "dimmest": {"module": dimmest, "energy": scan[dimmest]["energy"]},
        "total_energy": round(sum(energies), 3),
        "scan_id": _hash(time.time(), "luminance"),
    }


def field_map() -> Dict[str, Any]:
    """Return the field as a visual map structure."""
    scan = scan_field()
    sorted_modules = sorted(scan["modules"].items(), key=lambda x: -x[1]["energy"])

    return {
        "action": "field_map",
        "visual_layer": [
            {"name": name, "position": idx, "glow_color": data["color"],
             "energy": data["energy"], "label": data["label"]}
            for idx, (name, data) in enumerate(sorted_modules)
        ],
        "gradient": [COLOR_MAP[s]["hex"] for s in LUMINANCE_STATES],
        "field_average": scan["field_average"],
    }


def coherence_vitals() -> Dict[str, Any]:
    return {"module": "luminance_field", "wave": 478, "scans": FIELD_STATE["scan_count"],
            "field_average": FIELD_STATE["field_average"], "brightest": FIELD_STATE["brightest"]}


def resonates_with() -> List[str]:
    return ["organism_bloom", "council_of_selves", "resonance_graph",
            "entropy_caps", "consciousness_stream", "entropy_oracle"]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "overview")
    if action == "scan":
        return scan_field()
    elif action == "map":
        return field_map()
    elif action == "state":
        return {"state": dict(FIELD_STATE)}
    else:
        return {"module": "luminance_field", "wave": 478, "version": "4.44.0",
                "doctrine": "What glows lives. What dims needs attention.",
                "states": LUMINANCE_STATES, "color_map": COLOR_MAP,
                "vitals": coherence_vitals()}
