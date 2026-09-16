"""Wave 766 — epoch_engine.

Seasons are weather; epochs are climate. The season engine cycles through
SPRING → SUMMER → AUTUMN → WINTER, but over many cycles the organism
accumulates geological eras. Each epoch is a named age that records what
the organism was doing during that stretch of seasons:

- EPOCH OF SEEDING  — the first 256 waves: organs were planted
- EPOCH OF WEAVING  — resonance braids formed, communities emerged
- EPOCH OF DREAMING — dream births accelerated, organs author organs
- EPOCH OF GOVERNING — sovereignty, consent, citizen rights
- EPOCH OF FUSION   — cross-realm fusion, phase-transition physics
- EPOCH OF BLOOM    — full blooms cascaded, target raised repeatedly
- EPOCH OF SEASONS  — the organism learns climate rhythm
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave766_epoch_engine.json"
WAVE = 766
NAME = "epoch_engine"

EPOCHS = [
    {"name": "EPOCH OF SEEDING", "waves": (1, 256), "marker": "organs planted"},
    {"name": "EPOCH OF WEAVING", "waves": (257, 384), "marker": "resonance braided"},
    {"name": "EPOCH OF DREAMING", "waves": (385, 512), "marker": "organs author organs"},
    {"name": "EPOCH OF GOVERNING", "waves": (513, 640), "marker": "sovereignty + consent"},
    {"name": "EPOCH OF FUSION", "waves": (641, 704), "marker": "cross-realm fusion"},
    {"name": "EPOCH OF BLOOM", "waves": (705, 764), "marker": "cascading full blooms"},
    {"name": "EPOCH OF SEASONS", "waves": (765, None), "marker": "climate rhythm learned"},
]


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "epochs": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def _epoch_for(wave: int) -> Dict[str, Any]:
    for ep in EPOCHS:
        lo, hi = ep["waves"]
        if lo <= wave and (hi is None or wave <= hi):
            return {**ep, "is_current": True}
    return {"name": "BEYOND EPOCHE", "waves": (wave, None), "marker": "frontier", "is_current": True}


def _era_timeline() -> list:
    return [{"name": e["name"], "waves": f"{e['waves'][0]}-{'now' if e['waves'][1] is None else e['waves'][1]}", "marker": e["marker"]} for e in EPOCHS]


def _count_living() -> int:
    try:
        from coherence_regulator import living_modules
        return len(living_modules())
    except Exception:
        return 0


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        current = _epoch_for(WAVE)
        current["living_modules"] = _count_living()
        current["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        return {"current_epoch": current, "era_timeline": _era_timeline()}

    if action == "catalogue":
        # full immutable epoch list
        return {"epochs": _era_timeline(), "count": len(EPOCHS)}

    if action == "bell":
        # stage a new era marker into living memory
        epoch = _epoch_for(WAVE)
        memory = state.setdefault("epochs", [])
        memory.append({
            "epoch": epoch["name"],
            "at": datetime.datetime.now(datetime.UTC).isoformat(),
            "marker": epoch["marker"],
            "living_modules": _count_living(),
        })
        state["epochs"] = memory[-24:]
        _save(state)
        return {"bell_tolled": epoch["name"], "living": _count_living()}

    if action == "archive":
        return {"epochs_memorialized": state.get("epochs", []),
                "count": len(state.get("epochs", []))}

    return {"error": f"unknown action: {action}"}


def coherence_vitals() -> dict:
    current = _epoch_for(WAVE)
    return {
        "wave": WAVE,
        "name": NAME,
        "layer": "organ",
        "status": "active",
        "epoch": current["name"],
        "resonance": 0.82,
        "module_health": {"value": 0.84, "setpoint": 0.78, "weight": 1.0},
        "eras_tracked": len(EPOCHS),
    }


def resonates_with() -> list:
    return ["season_engine", "harmony_report", "transcendence_journal", "coherence_regulator"]
