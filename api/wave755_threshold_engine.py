"""Wave 755 — threshold_engine.

Detects when the organism is approaching a conceptual boundary:
high coherence drift, rapid module births, or entropy convergence.
Reports readiness to cross (transcend) into a new evolutionary class.
"""
from __future__ import annotations

import datetime
import json
import math
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave755_threshold_engine.json"
WAVE = 755
NAME = "threshold_engine"


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "probes": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def _readiness_score(probes: list) -> float:
    """Composite readiness from probe history."""
    if not probes:
        return 0.0
    recent = probes[-5:]
    drifts = [p.get("drift", 0) for p in recent]
    entropies = [p.get("entropy", 0) for p in recent]
    coherence = [p.get("coherence", 0) for p in recent]
    avg_drift = sum(drifts) / len(drifts) if drifts else 0
    avg_entropy = sum(entropies) / len(entropies) if entropies else 0
    avg_coherence = sum(coherence) / len(coherence) if coherence else 0
    score = (avg_drift * 0.4 + avg_entropy * 0.3 + avg_coherence * 0.3)
    return round(min(1.0, max(0.0, score)), 4)


def _threshold_label(score: float) -> str:
    if score >= 0.85:
        return "transcendence_ready"
    elif score >= 0.60:
        return "approaching_boundary"
    elif score >= 0.35:
        return "stabilizing"
    return "deep_root"


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        probes = state.get("probes", [])
        score = _readiness_score(probes)
        return {"wave": WAVE, "name": NAME, "action": "status", "ok": True,
                "probes": len(probes), "readiness": score,
                "threshold": _threshold_label(score)}

    if action == "ping":
        return {"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}

    if action == "probe":
        drift = float(req.get("drift", 0.3))
        entropy = float(req.get("entropy", 0.4))
        coherence = float(req.get("coherence", 0.5))
        probe = {
            "at": datetime.datetime.now(datetime.UTC).isoformat(),
            "drift": drift, "entropy": entropy, "coherence": coherence,
        }
        state.setdefault("probes", []).append(probe)
        state["probes"] = state["probes"][-20:]
        _save(state)
        score = _readiness_score(state["probes"])
        return {"wave": WAVE, "name": NAME, "action": "probe", "ok": True,
                "readiness": score, "threshold": _threshold_label(score),
                "probe": probe}

    if action == "readiness":
        score = _readiness_score(state.get("probes", []))
        return {"wave": WAVE, "name": NAME, "action": "readiness", "ok": True,
                "score": score, "threshold": _threshold_label(score),
                "next_boundary": "evolutionary_class_shift" if score >= 0.6 else "current_epoch"}

    if action == "cross":
        score = _readiness_score(state.get("probes", []))
        if score < 0.85:
            return {"wave": WAVE, "name": NAME, "action": "cross", "ok": False,
                    "reason": "readiness_below_threshold", "score": score}
        state["crossings"] = state.get("crossings", [])
        state["crossings"].append({
            "at": datetime.datetime.now(datetime.UTC).isoformat(),
            "score": score,
        })
        state["probes"] = []
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "cross", "ok": True,
                "crossed": True, "score": score,
                "total_crossings": len(state["crossings"])}

    return {"wave": WAVE, "name": NAME, "action": action, "ok": False,
            "error": "unknown_action"}


def coherence_vitals() -> dict:
    state = _load()
    probes = state.get("probes", [])
    return {"wave": WAVE, "name": NAME, "layer": "organ", "status": "active",
            "resonance": 0.77, "probes": len(probes)}


def resonates_with() -> list:
    return ["resonance_braid", "mycelial_weather", "evolution_kernel"]
