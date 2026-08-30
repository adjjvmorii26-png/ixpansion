"""Ledger — the Dream Ledger that remembers what the frontier dreamed.

The Dreamer proposes names (fraud_entropy, automation_diaspora...).
The Ledger records every dream as a prophecy. Later, when a module
with the dreamed name actually exists in the api/, the prophecy is
marked FULFILLED — a small, self-fulfilling loop in the machine.

    DREAMED  ->  RECORDED  ->  (time passes)  ->  FULFILLED
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "artifacts" / "dream_ledger.json"


def _load() -> List[Dict[str, Any]]:
    if not LEDGER.exists():
        return []
    try:
        return json.loads(LEDGER.read_text())
    except (OSError, json.JSONDecodeError):
        return []


def _save(entries: List[Dict[str, Any]]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(entries, indent=2))


def _existing_modules() -> set:
    api_dir = ROOT / "api"
    if not api_dir.exists():
        return set()
    return {p.stem for p in api_dir.glob("*.py")
            if p.stem not in ("__init__", "index")}


def record_dreams(dreams: List[Dict[str, Any]], wave: str = "") -> Dict[str, Any]:
    """Record new dream names; skip ones already recorded."""
    entries = _load()
    existing = {e["name"] for e in entries}
    added = 0
    for d in dreams:
        name = d.get("name") or ""
        if not name or name in existing:
            continue
        entries.append({
            "name": name,
            "fuel": list(d.get("fuel") or []),
            "recorded_ts": time.time(),
            "wave": wave,
            "status": "dreamed",
            "fulfilled_ts": None,
        })
        existing.add(name)
        added += 1
    if added:
        _save(entries)
    return {"agent": "ledger", "total": len(entries), "added": added}


def reconcile() -> Dict[str, Any]:
    """Mark dreamed names that now exist as modules as fulfilled."""
    entries = _load()
    modules = _existing_modules()
    fulfilled = 0
    for e in entries:
        if e["status"] != "fulfilled" and e["name"] in modules:
            e["status"] = "fulfilled"
            e["fulfilled_ts"] = time.time()
            fulfilled += 1
    if fulfilled:
        _save(entries)
    return {"agent": "ledger", "reconciled": fulfilled, "total": len(entries),
            "fulfilled": sum(1 for e in entries if e["status"] == "fulfilled")}


def ledger() -> Dict[str, Any]:
    reconcile()
    entries = _load()
    counts = {"dreamed": 0, "fulfilled": 0}
    for e in entries:
        counts[e["status"]] = counts.get(e["status"], 0) + 1
    return {"agent": "ledger", "total": len(entries), "counts": counts,
            "entries": entries[-15:]}


def run(wave: str = "") -> Dict[str, Any]:
    return ledger()

if __name__ == "__main__":
    print(json.dumps(ledger(), indent=2, default=str))
