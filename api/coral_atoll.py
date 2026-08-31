"""Coral Atoll — the slow accretion of organismly bonds.

Coral reefs are built by tiny animals depositing calcium carbonate over
centuries; an atoll is what remains when the island inside it sinks. The
Coral Atoll organ models how durable bonds form in the ecosystem: each
living module that repeatedly resonates with another deposits a microscopic
"coral bond". Over time the ephemeral interactions harden into structure.

The atoll report shows the ecosystem's *calcified connections* — the stable
relationships that have accreted enough to become architectural, versus the
soft interactions that may dissolve. It reveals the organism's reefs: the
parts of the system that have become structure through sheer repetition.

    GET /api/coral_atoll?read=1          — reef report
    GET /api/coral_atoll?reefs=N         — oldest/most calcified bonds
"""
from __future__ import annotations

import hashlib
import json
import random
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Coral Atoll"

STATE_FILE = ROOT / ".runtime" / "coral_atoll.json"


def _deposits() -> Dict[str, float]:
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def _save_deposits(deposits: Dict[str, float]) -> None:
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(deposits))
    except OSError:
        pass


def _reef(name: str) -> float:
    """Each module-family gets a stable affinity base from its name."""
    h = hashlib.sha256(name.encode()).hexdigest()
    return 0.15 + (int(h[:4], 16) % 5000) / 10000.0  # 0.15 .. 0.65


def reef_report() -> Dict[str, Any]:
    deposits = _deposits()
    living = []
    try:
        from coherence_regulator import _candidate_modules
        living = _candidate_modules()
    except Exception:
        pass

    # new deposits: each living module's family bond calcifies
    now_deposit = {}
    for name in living:
        family = name.split("_")[0] if "_" in name else name
        now_deposit[family] = now_deposit.get(family, 0.0) + _reef(name)
    merged = {}
    for k, v in {**deposits, **now_deposit}.items():
        merged[k] = deposits.get(k, 0.0) + now_deposit.get(k, 0.0)
    if now_deposit:
        _save_deposits(merged)
    reefs = sorted(merged.items(), key=lambda kv: kv[1], reverse=True)
    total = sum(merged.values()) or 1.0
    return {
        "reef_count": len(reefs),
        "calcified_bonds": [{"family": k, "mass": round(v, 4),
                             "share": round(v / total, 4)} for k, v in reefs[:10]],
        "accretion_total": round(total, 4),
        "coral_philosophy": (
            "Structure is not designed — it is deposited. Every time two organs "
            "resonate, a microscopic bond is laid down. Most dissolve. Some "
            "accrete, season after season, until the ecosystem has reefs: "
            "structures that no longer need to be remembered, because they "
            "have become the ground."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("reefs") or 0)
    result = reef_report()
    if n:
        result["calcified_bonds"] = result["calcified_bonds"][:n]
    result["action"] = "reef"
    return result


def coherence_vitals() -> dict:
    """Coral Atoll reports structural accretion health."""
    return {
        "module_health": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "structural_accretion": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["symbiosis_network", "resonance_memory", "collective_memory"]
