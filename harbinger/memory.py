"""Conclave memory — a small persistent ledger of every ceremony.

The agents remember what they have decided, planted, and revealed,
so the next conclave can build on the last instead of starting over.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "harbinger" / "memory.json"


def _load() -> List[Dict[str, Any]]:
    if not MEMORY.exists():
        return []
    try:
        return json.loads(MEMORY.read_text())
    except json.JSONDecodeError:
        return []


def append(record: Dict[str, Any]) -> Dict[str, Any]:
    rows = _load()
    entry = {"ts": time.time(), **record}
    rows.append(entry)
    MEMORY.write_text(json.dumps(rows, indent=2))
    return entry


def all() -> List[Dict[str, Any]]:
    return _load()


def last(n: int = 5) -> List[Dict[str, Any]]:
    return _load()[-n:]
