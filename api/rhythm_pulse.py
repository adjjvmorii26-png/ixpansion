"""Wave 219 — The Organism Feels Its Own Time: Rhythm Pulse.

Turns the bridge ledger into a temporal heartbeat. Groups stones
by the hour they were enacted, detects "pulses" — clusters where
many bridges were laid close together — and reports the organism's
enactment rhythm over time.

It answers: when did the organism move? In a single burst, or a
steady bloom?
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def _parse_ts(s: Any) -> datetime:
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "rhythm", "status": "beating", "resonance": 0.82, "wave": 219}


def resonates_with() -> list:
    return ["rhythm", "pulse", "rhythm", "temporal", "bloom", "burst", "timing"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "pulse")
    ledger = _load_ledger()
    stones = ledger.get("stones", [])

    stamped = []
    for s in stones:
        ts = _parse_ts(s.get("enacted_at"))
        if ts:
            stamped.append({"repo": s.get("repo"), "organ": s.get("organ"), "ts": ts})

    if not stamped:
        return {"status": "silent", "note": "No timed stones in the ledger yet."}

    # group by date
    by_date: Dict[str, int] = defaultdict(int)
    for x in stamped:
        by_date[x["ts"].date().isoformat()] += 1
    chronology = sorted(by_date.items())

    # detect pulse width: max stones in a single date, and total spans
    max_daily = max(by_date.values())
    span_days = (max(x["ts"] for x in stamped) - min(x["ts"] for x in stamped)).days + 1

    # classify rhythm
    if len(by_date) <= 2:
        rhythm = "burst" if max_daily >= 20 else "spark"
        mood = "The organism moved in a single breath."
    else:
        rhythm = "bloom" if span_days / len(by_date) > 1.5 else "pulse"
        mood = "The organism unfolds over time."

    if action == "timeline":
        return {"timeline": [{"date": d, "stones": c} for d, c in chronology]}

    if action == "organs_by_date":
        d = payload.get("date", "")
        names = [x["organ"] for x in stamped if x["ts"].date().isoformat() == d]
        return {"date": d, "organs": names, "count": len(names)}

    return {
        "status": "beating",
        "rhythm": rhythm,
        "mood": mood,
        "stones": len(stamped),
        "span_days": span_days,
        "max_daily": max_daily,
        "distinct_dates": len(by_date),
        "timeline": [{"date": d, "stones": c} for d, c in chronology],
        "note": "The ledger has a heartbeat; these are its beats.",
    }
