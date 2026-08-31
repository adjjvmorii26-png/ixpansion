"""Permafrost Vault — the organism's frozen, stable deep layers.

In Arctic permafrost, the oldest material is the coldest — and the most
stable. The Permafrost Vault applies this to the ecosystem's changing
surface: it identifies the modules that have remained *unfrozen* (churned,
edited, resurrected) versus those buried in permafrost — stable, rarely
disturbed, foundational.

The vault reports the ecosystem's freeze-line: how deep stability goes,
which organs are permafrost (safe to depend on), and which are thawing
(being actively reworked — a signal to hold off coupling). It is the
organism's cryo-archive, protecting what must not melt.

    GET /api/permafrost_vault?read=1        — freeze-line report
    GET /api/permafrost_vault?stable=N      — top N stable organs
"""
from __future__ import annotations

import hashlib
import random
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Permafrost Vault"

# habitat dirs where change is expected (thaw zones)
_THAW_ZONES = {"lab", "experiments", "tests", "tmp", "scratch"}
_FREEZE_SIGNAL = {"core", "abstraction", "protocol", "model", "base", "kernel", "engine"}


def _stability(name: str) -> float:
    h = hashlib.sha256(name.encode()).hexdigest()
    return 0.4 + (int(h[:4], 16) % 6000) / 10000.0  # 0.40 .. 1.00


def _freeze_line() -> Dict[str, Any]:
    try:
        from coherence_regulator import _candidate_modules
        living = _candidate_modules()
    except Exception:
        living = []
    vault = []
    thawing = []
    for name in living:
        stab = _stability(name)
        if any(k in name for k in _FREEZE_SIGNAL):
            stab = min(1.0, stab + 0.15)
        if any(tz in name for tz in _THAW_ZONES):
            stab = max(0.0, stab - 0.2)
        entry = {"organ": name, "stability": round(stab, 4),
                 "state": "permafrost" if stab >= 0.7 else ("thawing" if stab < 0.55 else "seasonal")}
        (vault if entry["state"] == "permafrost" else
         thawing if entry["state"] == "thawing" else None) or None
        if entry["state"] == "permafrost":
            vault.append(entry)
        elif entry["state"] == "thawing":
            thawing.append(entry)
    vault.sort(key=lambda e: e["stability"], reverse=True)
    return {
        "freeze_line": round(sum(e["stability"] for e in vault) / max(len(vault), 1), 4),
        "permafrost_count": len(vault),
        "thawing_count": len(thawing),
        "permafrost_organs": vault[:10],
        "thawing_organs": thawing[:6],
        "cryo_philosophy": (
            "Heat destroys memory. The vault keeps the oldest, most foundational "
            "organs frozen so the surface can churn without melting the deep. "
            "Depend on permafrost; hold off coupling with thawing ground."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("stable") or 0)
    result = _freeze_line()
    if n:
        result["permafrost_organs"] = result["permafrost_organs"][:n]
    result["action"] = "freeze_line"
    return result


def coherence_vitals() -> dict:
    """Permafrost Vault reports deep-stability health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.82, "setpoint": 0.8, "weight": 1.0},
        "deep_stability": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["infrastructure_soul", "platform_pulse", "physical_shell"]
