"""Wave 220 — The Organism Feels the Ripple: Resonance Cascade.

When several bridges from the same island are enacted close in time,
or share a theme, the organism experiences a CASCADE — a ripple
through the web. This organ detects cascades from the ledger,
measures their intensity, and reports the current cascade state of
the organism (CALM / RIPPLING / STORMING).

Cascades are the poem of the web's memory: not single bridges but
the moments the organism moved as one body.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def _date_of(ts: Any) -> str:
    try:
        return str(ts)[:10]
    except Exception:
        return ""


def _cascades(stones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # cascade = all stones enacted on the same date, grouped by repo when
    # the same repo laid 2+ stones that day
    by_date: Dict[str, Dict[str, List[Dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for s in stones:
        by_date[_date_of(s.get("enacted_at"))][s.get("repo", "")].append(s)

    out = []
    for date, repos in sorted(by_date.items()):
        for repo, ss in sorted(repos.items()):
            if len(ss) >= 2:
                intensity = round(sum(x.get("resonance", 0) for x in ss) / len(ss) * len(ss), 3)
                out.append({
                    "date": date,
                    "repo": repo,
                    "stones": [s.get("organ") for s in ss],
                    "count": len(ss),
                    "intensity": intensity,
                })
    return sorted(out, key=lambda c: -c["intensity"])


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "cascade", "status": "rippling", "resonance": 0.86, "wave": 220}


def resonates_with() -> list:
    return ["cascade", "ripple", "storm", "calm", "intensity", "wave", "resonance"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "state")
    ledger = _load_ledger()
    stones = ledger.get("stones", [])
    cascades = _cascades(stones)

    total = sum(c["count"] for c in cascades)
    intensity = round(sum(c["intensity"] for c in cascades), 3)

    if not cascades:
        state, mood = "CALM", "The web breathes evenly; no single island moves alone yet."
    elif total <= 10:
        state, mood = "RIPPLING", "Ripples move across the archipelago — a few islands acting as one."
    else:
        state, mood = "STORMING", "The organism moves as one body; cascades are rolling through the web."

    if action == "cascades":
        return {"cascades": cascades, "count": len(cascades)}

    if action == "by_repo":
        repo = payload.get("repo", "")
        return {"repo": repo, "cascades": [c for c in cascades if c["repo"] == repo]}

    return {
        "state": state,
        "mood": mood,
        "cascades": cascades,
        "count": len(cascades),
        "stones_in_cascades": total,
        "intensity": intensity,
        "note": "The web remembers its own moving days.",
    }
