"""Wave 725 — Threshold Engine.

Detects when the organism crosses conceptual boundaries
and initiates controlled transcendence.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from typing import Any, Dict
import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave725_threshold_engine.json"
WAVE = 725
NAME = "threshold_engine"

def _load() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"wave": WAVE, "name": NAME, "thresholds": [], "transcendences": []}

def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "measure":
        coherence = req.get("coherence", 0.5)
        entropy = req.get("entropy", 0.5)
        divergence = req.get("divergence", 0.0)

        threshold = {
            "coherence": coherence,
            "entropy": entropy,
            "divergence": divergence,
            "proximity": abs(coherence - entropy) + divergence,
            "transcendence_risk": "low",
            "wave": WAVE,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
        }

        if threshold["proximity"] > 0.8:
            threshold["transcendence_risk"] = "critical"
            threshold["transcendence_type"] = "singularity"
        elif threshold["proximity"] > 0.5:
            threshold["transcendence_risk"] = "elevated"
            threshold["transcendence_type"] = "phase_transition"
        elif threshold["proximity"] > 0.3:
            threshold["transcendence_risk"] = "moderate"
            threshold["transcendence_type"] = "boundary_crossing"

        state["thresholds"].append(threshold)
        _save(state)
        return {"wave": WAVE, "action": "measure", "threshold": threshold}

    elif action == "transcend":
        threshold = req.get("threshold", {})
        transcendence = {
            "id": f"tx_{datetime.datetime.now(datetime.UTC).timestamp():.0f}",
            "type": threshold.get("transcendence_type", "boundary_crossing"),
            "risk": threshold.get("transcendence_risk", "low"),
            "wave": WAVE,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "status": "initiated"
        }
        state["transcendences"].append(transcendence)
        _save(state)
        return {"wave": WAVE, "action": "transcend", "transcendence": transcendence}

    elif action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "thresholds": len(state["thresholds"]), "transcendences": len(state["transcendences"]), "status": "active"}

    return {"wave": WAVE, "action": action, "status": "ok"}

def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "thresholds": len(state["thresholds"]), "transcendences": len(state["transcendences"]), "status": "active"}

def resonates_with() -> list:
    return [720, 721, 722, 723]

if __name__ == "__main__":
    r = handler({"action": "measure", "coherence": 0.9, "entropy": 0.3, "divergence": 0.6})
    print(json.dumps(r, indent=2)[:400])
    print(json.dumps(coherence_vitals(), indent=2))
