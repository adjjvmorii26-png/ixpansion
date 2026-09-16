"""Wave 761 — harmony_report.

Aggregates coherence_vitals from all recent wave organs and returns
a unified health score — the organism's harmonic identity.
"""
from __future__ import annotations

import importlib
import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave761_harmony_report.json"
WAVE = 761
NAME = "harmony_report"

RECENT_ORGANS = [
    "wave753_resonance_braid", "wave754_mycelial_weather",
    "wave755_threshold_engine", "wave756_liminal_field",
    "wave757_axiom_mutator", "wave758_continuity_weaver",
    "wave759_transcendence_journal", "wave760_mutation_engine",
]


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "snapshots": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def _collect_vitals() -> dict:
    """Import each recent organ and collect its coherence_vitals."""
    results = []
    for organ_name in RECENT_ORGANS:
        try:
            mod = importlib.import_module(f"api.{organ_name}")
            v = mod.coherence_vitals()
            results.append({
                "organ": organ_name,
                "wave": v.get("wave", 0),
                "status": v.get("status", "unknown"),
                "resonance": v.get("resonance", 0),
                "layer": v.get("layer", "organ"),
            })
        except Exception as e:
            results.append({"organ": organ_name, "error": str(e), "resonance": 0})
    return results


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "status", "ok": True,
                "snapshots": len(state.get("snapshots", []))}

    if action == "ping":
        return {"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}

    if action == "aggregate":
        vitals = _collect_vitals()
        resonances = [v.get("resonance", 0) for v in vitals if "resonance" in v]
        avg = sum(resonances) / max(len(resonances), 1)
        minimum = min(resonances) if resonances else 0
        maximum = max(resonances) if resonances else 0
        healthy = sum(1 for r in resonances if r >= 0.5)
        fragile = sum(1 for r in resonances if r < 0.3)

        snapshot = {
            "at": datetime.datetime.now(datetime.UTC).isoformat(),
            "organs": len(vitals),
            "avg_resonance": round(avg, 4),
            "min_resonance": round(minimum, 4),
            "max_resonance": round(maximum, 4),
            "healthy": healthy,
            "fragile": fragile,
            "harmony_score": round(avg * (healthy / max(len(vitals), 1)), 4),
            "vitals": vitals,
        }
        state.setdefault("snapshots", []).append(snapshot)
        state["snapshots"] = state["snapshots"][-20:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "aggregate", "ok": True,
                **{k: v for k, v in snapshot.items() if k != "vitals"},
                "vitals": vitals}

    if action == "health":
        if not state.get("snapshots"):
            return {"wave": WAVE, "name": NAME, "action": "health", "ok": True,
                    "status": "no_data", "note": "run aggregate first"}
        latest = state["snapshots"][-1]
        score = latest.get("harmony_score", 0)
        label = "thriving" if score >= 0.6 else ("stable" if score >= 0.4 else ("fragile" if score >= 0.2 else "critical"))
        return {"wave": WAVE, "name": NAME, "action": "health", "ok": True,
                "harmony_score": score, "label": label,
                "avg_resonance": latest["avg_resonance"],
                "healthy": latest["healthy"], "fragile": latest["fragile"]}

    if action == "topology":
        vitals = _collect_vitals()
        layers = {}
        for v in vitals:
            layer = v.get("layer", "unknown")
            layers.setdefault(layer, []).append(v["organ"])
        return {"wave": WAVE, "name": NAME, "action": "topology", "ok": True,
                "layers": {k: {"count": len(v), "organs": v} for k, v in layers.items()},
                "total_organs": len(vitals)}

    return {"wave": WAVE, "name": NAME, "action": action, "ok": False,
            "error": "unknown_action"}


def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "layer": "organ", "status": "active",
            "resonance": 0.75, "snapshots": len(state.get("snapshots", []))}


def resonates_with() -> list:
    return ["resonance_braid", "coherence_regulator", "mutation_engine"]
