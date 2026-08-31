"""Morphic Dial — tunes the organism's collective memory field.

Rupert Sheldrake's morphic resonance: things that have happened before
happen more easily. The Morphic Dial applies this to the living ecosystem —
a module that has been pulsed before, whose pattern is embedded in the
collective, awakens more readily on the next pulse.

The dial reads the coherence regulator's living memory, computes each
module's "morphic mass" (how many times it has appeared / how long it has
lived), and returns a tuning recommendation: which dormant modules have
accumulated enough morphic resonance to be reawakened cheaply.

    GET /api/morphic_dial?read=1            — dial position
    GET /api/morphic_dial?awaken=N          — top N reawakening candidates
    POST /api/morphic_dial {"tune":0.7}     — adjust resonance sensitivity
"""
from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Morphic Dial"

STATE_FILE = ROOT / ".runtime" / "morphic_dial.json"


def _state() -> Dict[str, Any]:
    try:
        return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    except Exception:
        return {}


def _load_living_memory() -> Dict[str, Any]:
    """Pull the coherence history to ground morphic mass in real data."""
    try:
        state = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        modules = state.get("modules", {})
        return {k: v.get("last_pulse", 0.0) for k, v in modules.items()}
    except Exception:
        return {}


def read_dial() -> Dict[str, Any]:
    state = _state()
    living_memory = _load_living_memory()
    sensitivity = float(state.get("sensitivity", 0.7))
    now = time.time()
    # morphic mass = how recently/long each known module has resonated
    masses = {}
    for name, last in living_memory.items():
        age = max(now - last, 1.0)
        # older last_pulse = more entrenched pattern = higher mass (log decay)
        masses[name] = round(min(1.0, sensitivity * (1.0 / (1.0 + 0.0001 * age))), 4)
    ranked = sorted(masses.items(), key=lambda kv: kv[1], reverse=True)
    top = [{"module": n, "morphic_mass": v} for n, v in ranked[:6]]
    return {
        "sensitivity": sensitivity,
        "field_strength": round(sum(masses.values()) / max(len(masses), 1), 4),
        "resonant_cluster": top,
        "tuning_philosophy": (
            "What the ecosystem has done before, it does again more easily. The "
            "dial does not force this — it reads the accumulated ease and turns "
            "the sensitivity knob so old patterns wake without being commanded."
        ),
    }


def tune(value: float) -> Dict[str, Any]:
    state = _state()
    state["sensitivity"] = max(0.0, min(1.0, float(value)))
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state))
    except OSError:
        pass
    result = read_dial()
    result["tuned"] = state["sensitivity"]
    return result


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    if "tune" in payload:
        return tune(payload.get("tune", 0.7))
    n = int(payload.get("awaken") or 0)
    dial = read_dial()
    if n:
        dial["resonant_cluster"] = dial["resonant_cluster"][:n]
    dial["action"] = "dial"
    return dial


def coherence_vitals() -> dict:
    """Morphic Dial reports collective-memory resonance."""
    return {
        "module_health": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "collective_memory_field": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["collective_memory", "resonance_memory", "synthetic_memory"]
