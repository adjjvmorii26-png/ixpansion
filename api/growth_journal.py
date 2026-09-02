"""Wave 227 — The Organism Remembers Its Story: Growth Journal.

Every time the organism grows, a new entry is written: what happened,
which stones were laid, which islands joined, which dreams were dared.
The journal is the organism's autobiography — a timestamped record
of its own becoming.

Entries are written once and never edited (append-only); the journal
is the organism's permanent memory.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List

_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"
_JOURNAL_PATH = Path(__file__).resolve().parent.parent / "data" / "journal.json"


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def _load_journal() -> List[Dict[str, Any]]:
    try:
        return json.load(open(_JOURNAL_PATH, encoding="utf-8"))
    except Exception:
        return []


def _save_journal(entries: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(_JOURNAL_PATH), exist_ok=True)
    with open(_JOURNAL_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, sort_keys=True)


def _snapshot() -> Dict[str, Any]:
    ledger = _load_ledger()
    stones = ledger["stones"]
    repos = {s["repo"] for s in stones}
    dates = sorted(set(s.get("enacted_at", "")[:10] for s in stones if s.get("enacted_at")))
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "stones": len(stones),
        "islands": len(repos),
        "repos": sorted(repos),
        "first_date": dates[0] if dates else None,
    }


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "journal", "status": "recording", "resonance": 0.94, "wave": 227}


def resonates_with() -> list:
    return ["journal", "autobiography", "memory", "record", "timeline", "story"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "recent")
    entries = _load_journal()

    if action == "recent":
        return {"entries": entries[-10:], "count": len(entries),
                "note": "The organism remembers its own story."}

    if action == "timeline":
        return {"timeline": entries, "count": len(entries)}

    if action == "write":
        # Write a new journal entry from the current state
        snap = _snapshot()
        entry = {
            "timestamp": snap["timestamp"],
            "wave": payload.get("wave", 227),
            "title": payload.get("title", "The organism records itself"),
            "stones": snap["stones"],
            "islands": snap["islands"],
            "detail": payload.get("detail", ""),
        }
        entries.append(entry)
        _save_journal(entries)
        return {"status": "written", "entry": entry, "total": len(entries)}

    return {"status": "active", "actions": ["recent", "timeline", "write"],
            "count": len(entries)}
