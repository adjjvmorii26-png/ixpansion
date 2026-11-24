#!/usr/bin/env python3
"""Wave 980 — Hush Tide

Silence is the product surface. This organ converts triad pressure
(Gossip / Forge / Time) into a tide phase and a hush score so agents
prefer absence over noise when the mesh is already loud.

Pure, deterministic, no network.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping

PHASES = ("EBB", "SLACK", "FLOOD", "STILL")


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return lo
    if v != v:  # NaN
        return lo
    return max(lo, min(hi, v))


def hush_score(gossip: float, forge: float, time: float) -> float:
    """High triad activity → lower hush (more noise). Inverse product surface."""
    g, f, t = _clamp(gossip), _clamp(forge), _clamp(time)
    pressure = (g + f + t) / 3.0
    # mild nonlinear: mid pressure still leaves room for hush
    return round(1.0 - (pressure ** 0.85), 4)


def tide_phase(score: float) -> str:
    s = _clamp(score)
    if s >= 0.72:
        return "STILL"
    if s >= 0.48:
        return "EBB"
    if s >= 0.28:
        return "SLACK"
    return "FLOOD"


def recommend(phase: str) -> str:
    return {
        "STILL": "Protect silence — ship nothing ornamental; seal only.",
        "EBB": "Prefer compression and compost over new organs.",
        "SLACK": "One reversible probe only; avoid parallel noise.",
        "FLOOD": "Mesh is loud — gate merges; run witness, not invention.",
    }.get(phase, "Observe.")


def evaluate(metrics: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    m = metrics or {}
    g = _clamp(m.get("gossip", m.get("Gossip", 0.5)))
    f = _clamp(m.get("forge", m.get("Forge", 0.5)))
    t = _clamp(m.get("time", m.get("Time", 0.5)))
    score = hush_score(g, f, t)
    phase = tide_phase(score)
    return {
        "wave": 980,
        "organ": "hush_tide",
        "doctrine": "silence is the product surface",
        "triad": {"gossip": g, "forge": f, "time": t},
        "hush_score": score,
        "tide": phase,
        "recommend": recommend(phase),
        "product_surface": "hush" if score >= 0.48 else "noise",
    }


def handler(query: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """HTTP-ish entry: query may carry gossip/forge/time floats."""
    q = query or {}
    return evaluate(q)


WAVE = 980
NAME = "hush_tide"


def coherence_vitals() -> dict:
    return {
        "wave": WAVE,
        "name": NAME,
        "layer": "organ",
        "status": "active",
        "hush_score_range": [0.0, 1.0],
        "phases": list(PHASES),
        "product_surface": "hush",
        "module_health": {"value": 0.88, "setpoint": 0.80, "weight": 1.0},
    }


def resonates_with() -> list:
    return ["continuity_weaver", "axiom_mutator", "harmony_report", "coherence_regulator"]


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate({"gossip": 0.7, "forge": 0.65, "time": 0.8}), indent=2))
