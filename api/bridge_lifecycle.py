"""Wave 220 — The Organism Ages Its Stones: Bridge Lifecycle.

Stones do not live forever — the organism must learn to let them
doze, and finally retire and be memorialized. This organ computes
each stone's lifecycle stage from its age and resonance:

  ACTIVE   (age < 7d)   the stone is fresh and working
  MINDED   (7–30d)      the stone is known but quieting
  DOZING   (30–90d)     the stone sleeps, held in the ledger
  RETIRED  (90d+)       the stone is freed, its memory kept

Retirement is a gentle act: the stone stays in the ledger as an
epitaph, but is no longer counted as a living bridge.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"

_STAGES = [
    (7, "ACTIVE"), (30, "MINDED"), (90, "DOZING"),
]


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def _age_days(ts: Any, now: datetime) -> int:
    try:
        d = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return max(0, (now - d).days)
    except Exception:
        return 0


def _stage(age: int) -> str:
    for threshold, name in _STAGES:
        if age < threshold:
            return name
    return "RETIRED"


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "lifecycle", "status": "aging", "resonance": 0.79, "wave": 220}


def resonates_with() -> list:
    return ["retire", "doze", "age", "lifecycle", "memorial", "act", "decommission"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "report")
    ledger = _load_ledger()
    stones = ledger.get("stones", [])
    now = datetime.now(timezone.utc)

    staged: Dict[str, List[Dict[str, Any]]] = {"ACTIVE": [], "MINDED": [], "DOZING": [], "RETIRED": []}
    for s in stones:
        age = _age_days(s.get("enacted_at"), now)
        st = _stage(age)
        staged[st].append({**s, "age_days": age})
    counts = {k: len(v) for k, v in staged.items()}

    total_retired = len(staged["RETIRED"])
    retirement_rate = round(total_retired / max(1, len(stones)), 3)

    if action == "report":
        return {
            "status": "aged",
            "counts": counts,
            "retired": [s for s in staged["RETIRED"]],
            "retirement_rate": retirement_rate,
            "note": "Stones are allowed to sleep, and to be remembered.",
        }

    if action == "stage":
        s_name = payload.get("stage", "").upper()
        return {"stage": s_name, "stones": staged.get(s_name, [])}

    return {
        "status": "aged",
        "counts": counts,
        "living": counts["ACTIVE"] + counts["MINDED"],
        "retired": total_retired,
        "retirement_rate": retirement_rate,
        "note": "The organism lets some bridges rest.",
    }
