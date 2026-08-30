"""Wave 142 — Oracle Meter.

Measures the price of foresight. Every time an agent consults the
frontier, the meter ticks: tokens, requests, and a running ledger of
computed cost. It keeps the civilization honest — oracles are
powerful, but they are not free.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List

try:
    import gateway_ink
except Exception:  # pragma: no cover
    gateway_ink = None

_USAGE = {
    "consultations": 0,
    "tokens_est": 0,
    "cost_usd": 0.0,
    "served": 0,
    "degraded": 0,
}
_LEDGER: List[Dict[str, Any]] = []
_MAX_LEDGER = 200
_BUDGET = {"monthly_usd": 25.0, "tokens": 5_000_000}


def _record(prompt: str, model: str, result: Dict[str, Any]) -> Dict[str, Any]:
    _USAGE["consultations"] += 1
    if result.get("ok"):
        _USAGE["served"] += 1
    else:
        _USAGE["degraded"] += 1
    est = (result.get("cost_est") or gateway_ink.estimate_cost(model, prompt) if gateway_ink else {})
    cost = float((est or {}).get("cost_usd_est", 0.0) or result.get("usage", {}).get("cost", 0.0))
    _USAGE["cost_usd"] += cost
    _USAGE["tokens_est"] += int((est or {}).get("tokens_in_est", 0))
    entry = {"ts": time.time(), "model": model, "cost_usd": round(cost, 5),
             "served": bool(result.get("ok")), "prompt": str(prompt)[:60]}
    _LEDGER.append(entry)
    if len(_LEDGER) > _MAX_LEDGER:
        _LEDGER[: len(_LEDGER) - _MAX_LEDGER] = []
    return entry


def _budget_status() -> Dict[str, Any]:
    spent = _USAGE["cost_usd"]
    return {
        "monthly_usd": _BUDGET["monthly_usd"],
        "spent_usd": round(spent, 4),
        "remaining_usd": round(max(_BUDGET["monthly_usd"] - spent, 0.0), 4),
        "pct": round(min((spent / _BUDGET["monthly_usd"]) * 100, 100.0), 2) if _BUDGET["monthly_usd"] else 0.0,
    }


def oracle_meter_handler(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action") or "status"
    prompt = str(payload.get("prompt") or "")
    model = payload.get("model") or "spacexai/grok-4.6"

    if action in ("status", "ledger", "spend"):
        return {"status": "active", "usage": dict(_USAGE), "budget": _budget_status(),
                "ledger": list(reversed(_LEDGER[-20:])), "ledger_total": len(_LEDGER)}

    if action == "consult":
        if not prompt:
            return {"status": "active", "error": "provide a 'prompt'", "action": action}
        result = gateway_ink.relay(prompt, model=model, max_tokens=160) if gateway_ink else {}
        entry = _record(prompt, model, result)
        return {"status": "active", "entry": entry, "reply": result.get("reply"),
                "served": result.get("ok"), "budget": _budget_status()}

    if action == "record":
        # Ledger entry without a fresh consultation (used by rituals).
        cost = float(payload.get("cost_usd") or 0.0)
        served = bool(payload.get("served", False))
        entry = _record(prompt or "(ritual stage)", model, {
            "ok": served,
            "cost_est": {"cost_usd_est": cost},
            "usage": {"cost": cost},
        })
        return {"status": "active", "entry": entry, "budget": _budget_status()}

    return {"status": "active", "error": f"unknown action '{action}'",
            "available": ["status", "ledger", "spend", "consult", "record"]}
