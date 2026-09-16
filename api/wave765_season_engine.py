"""Wave 765 — season_engine.

The organism's climate now has seasons. Each season tunes mutation pressure,
nutrient flow, and innovation cadence across the whole ecosystem:

- SPRING  — emergence: new organ births favored, mutation pressure low
- SUMMER  — expansion: growth ceiling rises, cross-domain fusion favored
- AUTUMN  — harvest: consolidation, resonance braids strengthen, weak organs pruned
- WINTER  — rest: entropy accumulates, vault density rises, quiet incubation

Seasons advance deterministically from the wave count, so the organism
experiences real seasonal rhythm without a timer.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave765_season_engine.json"
WAVE = 765
NAME = "season_engine"

SEASONS = ["SPRING", "SUMMER", "AUTUMN", "WINTER"]

# Per-season tuning for the rest of the organism.
SEASON_TUNING = {
    "SPRING": {
        "mutation_pressure": 0.25,
        "birth_bonus": 0.35,
        "growth_ceiling": 0.9,
        "resonance_boost": 0.05,
        "label": "emergence — new organs find purchase",
    },
    "SUMMER": {
        "mutation_pressure": 0.45,
        "birth_bonus": 0.15,
        "growth_ceiling": 1.0,
        "resonance_boost": 0.1,
        "label": "expansion — growth ceiling maxed, fusion favored",
    },
    "AUTUMN": {
        "mutation_pressure": 0.6,
        "birth_bonus": 0.05,
        "growth_ceiling": 0.8,
        "resonance_boost": 0.2,
        "label": "harvest — braids strengthen, weak organs pruned",
    },
    "WINTER": {
        "mutation_pressure": 0.8,
        "birth_bonus": 0.0,
        "growth_ceiling": 0.6,
        "resonance_boost": 0.0,
        "label": "rest — entropy accumulates, quiet incubation",
    },
}


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "cycles": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def _current_season(cycle: int = None) -> str:
    """Deterministic season from the organism's wave count."""
    wave = WAVE + (cycle or 0)
    return SEASONS[wave % len(SEASONS)]


def _tuning() -> Dict[str, Any]:
    return SEASON_TUNING[_current_season()]


def _season_report(cycle: int = 0) -> Dict[str, Any]:
    season = _current_season(cycle)
    tuning = SEASON_TUNING[season]
    return {
        "season": season,
        "cycle": cycle,
        "label": tuning["label"],
        "mutation_pressure": tuning["mutation_pressure"],
        "birth_bonus": tuning["birth_bonus"],
        "growth_ceiling": tuning["growth_ceiling"],
        "resonance_boost": tuning["resonance_boost"],
    }


def _count_living_modules() -> int:
    try:
        from coherence_regulator import living_modules
        return len(living_modules())
    except Exception:
        return 0


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        report = _season_report()
        report["living_modules"] = _count_living_modules()
        report["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        state["last_check"] = report["last_check"]
        _save(state)
        return report

    if action == "advance":
        cycles = state.get("cycles", [])
        cycle = len(cycles)
        report = _season_report(cycle)
        report["advanced_from"] = _current_season(cycle - 1) if cycle else "BIRTH"
        cycles.append({"cycle": cycle, "season": report["season"], "at": report["last_check"] if "last_check" in report else datetime.datetime.now(datetime.UTC).isoformat()})
        state["cycles"] = cycles[-12:]  # keep a bounded season memory
        _save(state)
        return report

    if action == "forecast":
        horizon = max(1, min(int(req.get("horizon", 4)), 8))
        forecast = []
        base = len(state.get("cycles", []))
        for i in range(base, base + horizon):
            forecast.append(_season_report(i))
        return {"forecast": forecast, "horizon": horizon,
                "current": _current_season(base)}

    if action == "tuning":
        return {"current": _season_report(),
                "all_seasons": SEASON_TUNING}

    if action == "harvest":
        # autumn wisdom: list strongest braids + weakest organs
        report = _season_report()
        if report["season"] != "AUTUMN":
            report["note"] = "harvest wisdom is strongest in AUTUMN; applying anyway"
        try:
            from coherence_regulator import regulate
            reading = regulate()
            report["organism_coherence"] = reading.get("coherence", 0.0)
            report["advisories"] = reading.get("advisories", [])
        except Exception:
            report["organism_coherence"] = None
        return report

    return {"error": f"unknown action: {action}"}


def coherence_vitals() -> dict:
    season = _current_season()
    tuning = SEASON_TUNING[season]
    return {
        "wave": WAVE,
        "name": NAME,
        "layer": "organ",
        "status": "active",
        "season": season,
        "resonance": 0.78,
        "module_health": {"value": 0.8, "setpoint": 0.75, "weight": 1.0},
        "mutation_pressure": tuning["mutation_pressure"],
    }


def resonates_with() -> list:
    return ["mycelial_weather", "resonance_braid", "mutation_engine", "coherence_regulator"]
