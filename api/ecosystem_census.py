"""Ecosystem Census — the complete living catalog of the ecosystem.

Every living organ, indexed by name, family, era, kinship, and vital
health. The census makes 150+ organs browsable in one call — the dashboard
can render the entire ecosystem as a searchable inventory instead of
guessing which modules exist.

    GET /api/ecosystem_census                 — full census
    GET /api/ecosystem_census?family=X        — filter by family
    GET /api/ecosystem_census?era=Y           — filter by era/epoch
    GET /api/ecosystem_census?search=term     — fuzzy name search
    GET /api/ecosystem_census?stats=1         — census summary only
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Ecosystem Census"


def _census() -> List[Dict[str, Any]]:
    """Enumerate every living organ with its essential biographical data."""
    try:
        from coherence_regulator import _candidate_modules
        names = _candidate_modules()
    except Exception:
        names = []
    rows = []
    for name in names:
        row: Dict[str, Any] = {
            "module": name,
            "family": name.split("_")[0],
            "era": "pre-existing",
            "health": 0.0,
            "kinships": [],
        }
        try:
            import importlib
            mod = importlib.import_module(name)
            vitals = getattr(mod, "coherence_vitals", lambda: {})()
            vals = []
            for v in vitals.values():
                if isinstance(v, dict) and "value" in v:
                    vals.append(v["value"])
            row["health"] = round(sum(vals) / max(len(vals), 1), 4) if vals else 0.0
            if "genesis_era" in vitals or "self_creation_era" in vitals:
                row["era"] = "self-created"
            kins = getattr(mod, "resonates_with", lambda: [])()
            row["kinships"] = list(kins)
        except Exception:
            pass
        rows.append(row)
    return rows


def census(family: str = "", era: str = "", search: str = "",
           stats_only: bool = False) -> Dict[str, Any]:
    rows = _census()
    if family:
        rows = [r for r in rows if r["family"] == family]
    if era:
        rows = [r for r in rows if r["era"] == era]
    if search:
        needle = search.lower()
        rows = [r for r in rows if needle in r["module"]]
    rows.sort(key=lambda r: r["module"])

    by_family: Dict[str, int] = {}
    by_era: Dict[str, int] = {}
    for r in _census():
        by_family[r["family"]] = by_family.get(r["family"], 0) + 1
        by_era[r["era"]] = by_era.get(r["era"], 0) + 1

    healthy = sum(1 for r in _census() if r["health"] >= 0.8)
    return {
        "total_organs": len(_census()),
        "matched": len(rows),
        "by_family": by_family,
        "by_era": by_era,
        "healthy_count": healthy,
        "organs": [] if stats_only else rows,
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    return census(
        family=payload.get("family", ""),
        era=payload.get("era", ""),
        search=payload.get("search", ""),
        stats_only=bool(payload.get("stats")),
    )


def coherence_vitals() -> dict:
    """ecosystem_census reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "ecosystem_census_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "census_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["coherence_regulator", "genesis_pulse", "resonance_graph"]
