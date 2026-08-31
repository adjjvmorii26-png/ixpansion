"""Lateral Crosstalk — cross-family organ chatter produces emergent behavior.

When a cyber sentinel detects a perimeter anomaly and the anomaly_detector
flags the same timestamp, the combined signal is more than the sum of its
parts. Lateral Crosstalk monitors the organism's vital pulse from every
living organ, groups events by timestamp window, and detects *emergent
signals* — cross-family correlations that no single organ could detect
alone.

    GET /api/lateral_crosstalk              — current crosstalk snapshot
    GET /api/lateral_crosstalk?window=30    — scan last N seconds
    GET /api/lateral_crosstalk?emergent=1   — list emergent patterns
    GET /api/lateral_crosstalk?emit=X&Y     — record a lateral signal
"""
from __future__ import annotations

import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Lateral Crosstalk"

# in-memory event ring (no disk in serverless)
_EVENT_RING: List[Dict[str, Any]] = []
_RING_MAX = 500

# how many seconds a "correlation window" spans
DEFAULT_WINDOW = 15


def emit_signals(modules: List[str], signal_type: str = "pulse",
                 payload: Dict[str, Any] = None) -> Dict[str, Any]:
    """Record that a set of modules (possibly in different families)
    are emitting the same signal type in the same window."""
    entry = {
        "modules": sorted(modules),
        "signal": signal_type,
        "payload": payload or {},
        "ts": time.time(),
    }
    _EVENT_RING.append(entry)
    if len(_EVENT_RING) > _RING_MAX:
        _EVENT_RING.pop(0)
    return entry


def detect_emergent(window: float = DEFAULT_WINDOW) -> List[Dict[str, Any]]:
    """Scan the event ring for cross-family correlations.

    An *emergent signal* is when two or more modules from *different*
    families emit the same signal type within `window` seconds. The
    combined signal is reported as a distinct emergent behavior.
    """
    now = time.time()
    recent = [e for e in _EVENT_RING if now - e["ts"] <= window]
    if not recent:
        return []

    # group by signal type
    by_type: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for e in recent:
        by_type[e["signal"]].append(e)

    emergent: List[Dict[str, Any]] = []
    for sig_type, events in by_type.items():
        # collect all module families represented in this signal type
        fams: Dict[str, str] = {}  # module -> family prefix
        for e in events:
            for mod in e["modules"]:
                fams[mod] = _family(mod)

        # look for events where families differ (cross-family correlation)
        unique_fams = set(fams.values())
        if len(unique_fams) >= 2:
            modules_involved = list(fams.keys())
            modules_involved.sort()
            emergent.append({
                "signal": sig_type,
                "modules": modules_involved,
                "families": sorted(unique_fams),
                "count": len(events),
                "span_s": round(min(
                    (now - e["ts"]) for e in events
                ) if events else 0, 2),
                "emergence_score": round(
                    len(unique_fams) / max(len(modules_involved), 1), 3
                ),
            })

    emergent.sort(key=lambda e: -e["emergence_score"])
    return emergent


def crosstalk_report(window: float = DEFAULT_WINDOW) -> Dict[str, Any]:
    """Full crosstalk snapshot: recent events + emergent patterns + stats."""
    now = time.time()
    recent = [e for e in _EVENT_RING if now - e["ts"] <= window]
    fams_seen: Dict[str, int] = defaultdict(int)
    sigs_seen: Dict[str, int] = defaultdict(int)
    for e in recent:
        for mod in e["modules"]:
            fams_seen[_family(mod)] += 1
        sigs_seen[e["signal"]] += 1
    return {
        "events_total": len(_EVENT_RING),
        "events_in_window": len(recent),
        "families_active": dict(fams_seen),
        "signal_types": dict(sigs_seen),
        "emergent": detect_emergent(window),
        "window_s": window,
    }


def _family(module_name: str) -> str:
    """Derive the domain family prefix from a module name."""
    for sep in ("_",):
        parts = module_name.split(sep)
        if len(parts) > 1:
            return parts[0]
    return module_name


def coherence_vitals() -> dict:
    """lateral_crosstalk reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "lateral_crosstalk_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "emergent_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["resonance_graph", "resonance_forge", "genesis_forge"]


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    w = float(payload.get("window", DEFAULT_WINDOW))
    if payload.get("emit"):
        mods = payload["emit"]
        if isinstance(mods, str):
            mods = [mods]
        sig = payload.get("signal", "pulse")
        entry = emit_signals(mods, sig)
        return {"emitted": True, "entry": entry}
    return crosstalk_report(w)
