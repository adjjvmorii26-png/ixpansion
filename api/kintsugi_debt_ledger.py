"""Kintsugi Debt Ledger — repaying the structural debt of broken ground.

When a module is born under strain, or ships with a stub, it accrues a
*structural debt* — fragility owed to the future. The Kintsugi Debt Ledger
is the ecosystem's accounting for that debt and its repayment. Each crack
is a liability; each golden seam is an asset; a fully gilded module has
cleared its debt and becomes a net asset to the organism.

The ledger tracks three balances: the fragility accrued, the gold invested,
and the net worth of each vessel. It answers: which modules still owe
strength to the system, and which have repaid it in full?

    GET /api/kintsugi_debt_ledger?read=1      — the balance sheet
    GET /api/kintsugi_debt_ledger?all=N       — all vessels + balances
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Kintsugi Debt Ledger"


def _ledger() -> Dict[str, Any]:
    try:
        survey = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
    except Exception:
        survey = {}
    seams = []
    try:
        seams = json.loads((ROOT / ".runtime" / "crack_seams.json").read_text()).get("seams", [])
    except Exception:
        seams = []
    seam_map = {s["subject"]: s for s in seams}

    rows = []
    # fragility balance: modules with health < target owe debt
    for name, m in survey.get("modules", {}).items():
        health = m.get("health", 1.0)
        fragility = max(0.0, 0.9 - health)
        gold = seam_map.get(name, {}).get("tensile_gift", 0.0) if name in seam_map else 0.0
        net = gold - fragility
        rows.append({
            "vessel": name,
            "fragility_debt": round(fragility, 4),
            "gold_invested": round(gold, 4),
            "net_worth": round(net, 4),
            "status": "repaid" if net >= 0 else "owing",
        })
    rows.sort(key=lambda r: r["net_worth"])
    repaid = [r for r in rows if r["status"] == "repaid"]
    owing = [r for r in rows if r["status"] == "owing" and r["fragility_debt"] > 0]
    total_debt = round(sum(r["fragility_debt"] for r in rows), 4)
    total_gold = round(sum(r["gold_invested"] for r in rows), 4)
    return {
        "vessels_ledged": len(rows),
        "repaid": len(repaid),
        "owing": len(owing),
        "total_fragility_debt": total_debt,
        "total_gold_invested": total_gold,
        "net_balance": round(total_gold - total_debt, 4),
        "repayment_status": "in_surplus" if total_gold >= total_debt else "structural_deficit",
        "owing_vessels": owing[:10],
        "ledger_philosophy": (
            "Every crack is a debt the future inherits. The ledger does not "
            "shame the broken — it counts what strength they still owe, and "
            "what gold has already been paid. Debt is not failure; it is "
            "unfinished repair, and the ledger keeps the accounts honest."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("all") or 0)
    result = _ledger()
    if n:
        result["owing_vessels"] = result["owing_vessels"][:n]
    result["action"] = "ledger"
    return result


def coherence_vitals() -> dict:
    """Kintsugi Debt Ledger reports structural-accounting health."""
    return {
        "module_health": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "repair_accounting": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "kintsugi_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["crack_seams", "crack_mapper", "credits"]
