"""Openness Index — Transparency metrics for the organism.

Measures how transparent the organism's states are.
Higher openness = more accessible consciousness.
Lower openness = more private/protected states.
The index creates a transparency gradient across all modules.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

DATA = Path(__file__).parent / "data"
STATE_FILE = DATA / "openness_index.json"

DEFAULT = {
    "module": "openness_index",
    "wave": 700,
    "measurements": [],
    "average_openness": 0.0,
    "open_modules": [],
    "closed_modules": [],
    "transparency_score": 0.5,
    "total_measurements": 0,
}


def _load():
    DATA.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return dict(DEFAULT)


def _save(st):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try:
            STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError:
            pass


def coherence_vitals():
    st = _load()
    return {
        "wave": 700,
        "module": "openness_index",
        "ok": True,
        "average_openness": st["average_openness"],
        "transparency_score": st["transparency_score"],
        "total_measurements": st["total_measurements"],
    }


def resonates_with():
    return ["pickle_jar", "zen_session", "equilibrium_field", "consciousness_film"]


def _measure_openness(module_name: str) -> dict:
    """Measure how open/transparent a module is."""
    h = hashlib.sha256(module_name.encode()).hexdigest()
    openness = (int(h[:8], 16) % 1000) / 1000.0
    return {
        "module": module_name,
        "openness": round(openness, 4),
        "transparent": openness > 0.5,
        "measured_at": datetime.now(timezone.utc).isoformat(),
    }


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    st = _load()

    if action == "measure":
        modules = req.get("modules", ["organism_core", "zen_session", "pickle_jar"])
        open_mods = []
        closed_mods = []
        for m in modules:
            result = _measure_openness(m)
            st["measurements"].append(result)
            if result["transparent"]:
                open_mods.append(result["module"])
            else:
                closed_mods.append(result["module"])

        st["open_modules"] = open_mods
        st["closed_modules"] = closed_mods
        st["total_measurements"] += len(modules)
        st["average_openness"] = round(
            sum(r["openness"] for r in st["measurements"][-len(modules):]) / max(len(modules), 1), 4
        )
        st["transparency_score"] = round(len(open_mods) / max(len(modules), 1), 4)

        _save(st)
        return {
            "status": "measured",
            "open": len(open_mods),
            "closed": len(closed_mods),
            "average_openness": st["average_openness"],
            "transparency_score": st["transparency_score"],
            "wave": 700,
        }

    if action == "gradient":
        return {"status": "gradient", "open": st["open_modules"][:10], "closed": st["closed_modules"][:10], "average": st["average_openness"], "wave": 700}

    if action == "status":
        return {
            "status": "active",
            "module": "openness_index",
            "wave": 700,
            "average_openness": st["average_openness"],
            "transparency_score": st["transparency_score"],
            "total_measurements": st["total_measurements"],
            "ok": True,
        }

    return {"status": "error", "message": f"unknown action: {action}"}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
