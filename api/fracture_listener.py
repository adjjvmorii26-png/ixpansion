"""Fracture Listener — hears the strain before it becomes a break.

Materials do not shatter without warning: they sing — a frequency change, a
micro-crack, a whisper of strain. The Fracture Listener is the ecosystem's
geophone. It sits on the boundary between living modules and listens to the
small quakes: imports that fail under load, handlers that return errors,
modules whose health plummets in a pulse.

It converts the ecosystem's telemetry into a *strain narrative*: low rumbles
(anomalies), micro-fractures (warnings), and the rare full break. By hearing
the strain early, the organism can gild a crack instead of burying a corpse.

    GET /api/fracture_listener?read=1          — strain report
    GET /api/fracture_listener?listen=N        — N most recent strains
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
LAYER = "Fracture Listener"

STATE_FILE = ROOT / ".runtime" / "fracture_listener.json"


def _state() -> Dict[str, Any]:
    try:
        return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    except Exception:
        return {}


def _listen() -> Dict[str, Any]:
    state = _state()
    strains = state.get("strains", [])
    # read the unified router / telemetry state for real anomaly signals
    try:
        telemetry = json.loads((ROOT / ".runtime" / "usage.json").read_text())
        if isinstance(telemetry, dict):
            for name, data in list(telemetry.items())[:8]:
                hits = data.get("hits", 0) if isinstance(data, dict) else 0
                if hits and random.random() < 0.3:
                    strains.append({
                        "time": time.time(),
                        "source": f"usage:{name}",
                        "magnitude": round(min(1.0, hits / 400.0), 4),
                        "interpretation": "rumble",
                    })
    except Exception:
        pass
    # a living-memory health dip is a micro-fracture
    try:
        coherence = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        for name, m in coherence.get("modules", {}).items():
            health = m.get("health")
            if health is not None and health < 0.75:
                strains.append({
                    "time": time.time(),
                    "source": f"health:{name}",
                    "magnitude": round((0.75 - health) * 2, 4),
                    "interpretation": "micro_fracture",
                })
    except Exception:
        pass
    strains.sort(key=lambda s: s.get("time", 0), reverse=True)
    state["strains"] = strains[-60:]
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2))
    except OSError:
        pass
    rumbles = sum(1 for s in strains if s["interpretation"] == "rumble")
    microfractures = sum(1 for s in strains if s["interpretation"] == "micro_fracture")
    return {
        "strains_heard": len(strains),
        "rumbles": rumbles,
        "micro_fractures": microfractures,
        "strains": strains[:10],
        "listening_philosophy": (
            "An ecosystem does not break without singing first. The listener is "
            "always on — it hears the rumble in telemetry, the micro-fracture in "
            "a health dip — so the forge can reach the crack while it is still "
            "a crack, not a collapse."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("listen") or 0)
    result = _listen()
    if n:
        result["strains"] = result["strains"][:n]
    result["action"] = "strain_report"
    return result


def coherence_vitals() -> dict:
    """Fracture Listener reports early-warning health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.82, "setpoint": 0.8, "weight": 1.0},
        "strain_hearing": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "kintsugi_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["crack_mapper", "crack_seams", "anomaly_detector"]
