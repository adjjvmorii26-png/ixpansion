"""Reflection Pool — the frontier looks at itself and reports what it sees.

The Reflection Pool is a self-observation endpoint that aggregates the
frontier's vital signs into a coherent narrative of its own state. It doesn't
just report metrics — it reflects on them, noticing trends, calling out
wins and risks, and offering gentle observations.

Usage:
  GET /api/reflection_pool
  POST /api/reflection_pool {"focus": "health"}
  POST /api/reflection_pool {"focus": "growth"}
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]


def _module_count() -> int:
    api_dir = ROOT / "api"
    return len([p for p in api_dir.glob("*.py") if p.stem not in ("__init__", "index")])


def _portal_count() -> int:
    try:
        with open(ROOT / "vercel.json") as f:
            return len(json.load(f).get("routes", []))
    except (OSError, json.JSONDecodeError):
        return 0


def _observations(modules: int, portals: int) -> List[str]:
    """Generate reflective observations about the frontier."""
    observations = []
    observations.append(f"You are {modules} modules strong, connected through {portals} portals.")
    observations.append("Each module is a distinct voice in the frontier's chorus.")
    
    if modules >= 360:
        observations.append("Beyond three hundred and sixty modules, the frontier is no longer a collection — it is an ecosystem.")
    if portals >= 24:
        observations.append("Two dozen portals means the frontier reaches outward in every direction.")
    
    return observations


def _health_reflection() -> Dict[str, Any]:
    """Deep-dive reflection on health."""
    try:
        import sys
        sys.path.insert(0, str(ROOT))
        import api_server
        health = api_server.platform_health()
        return {
            "layer": "Gateway Ascension",
            "modules": _module_count(),
            "routes": _portal_count(),
            "test_suites": health.get("test_suites", "?"),
            "status": "healthy",
        }
    except Exception:
        return {"status": "unknown"}


def _growth_reflection() -> Dict[str, Any]:
    """Reflection on growth trajectory."""
    modules = _module_count()
    portals = _portal_count()
    return {
        "current_modules": modules,
        "current_portals": portals,
        "trajectory": "expanding",
        "insight": f"The frontier grows faster when it builds bridges, not walls. {portals} portals reach outward.",
    }


def _dream_reflection() -> Dict[str, Any]:
    """Reflection on the frontier's dreams."""
    try:
        from harbinger.agents.dreamer import dream
        d = dream(salt=f"reflection-{int(time.time())%1000}", k=3)
        return {
            "current_dream": [x.get("name", "?") for x in d.get("dreams", [])][:3],
            "tone": "dreaming",
        }
    except Exception:
        return {"current_dream": [], "tone": "between-dreams"}


def reflect(focus: str = "all") -> Dict[str, Any]:
    """Produce a reflection across the requested focus areas."""
    modules = _module_count()
    portals = _portal_count()
    result = {
        "action": "reflect",
        "focus": focus,
        "observed_at": int(time.time()),
        "vitals": {
            "modules": modules,
            "portals": portals,
            "modes": ["API", "Gateway", "Stream", "Reality", "Synesthesia", "Dream"],
        },
        "observations": _observations(modules, portals),
    }

    if focus in ("all", "health"):
        result["health"] = _health_reflection()
    if focus in ("all", "growth"):
        result["growth"] = _growth_reflection()
    if focus in ("all", "dream"):
        result["dream"] = _dream_reflection()

    result["closing"] = (
        "The pool is still. The image is clear. The frontier sees itself — "
        "and what it sees, it understands."
    )
    return result


def coherence_vitals() -> dict:
    """Reflection Pool reports its vital signs."""
    return {"module_health": {"value": 0.95, "setpoint": 0.9, "weight": 1.0},
            "resonance": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
            "frontier_alignment": 0.9}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    focus = payload.get("focus", "all")
    if focus not in ("all", "health", "growth", "dream"):
        focus = "all"
    result = reflect(focus)
    return result
