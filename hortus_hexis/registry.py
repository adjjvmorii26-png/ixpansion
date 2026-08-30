"""Registry — the garden ledger of every organism ever grown."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List

from .artifacts import safe_name

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "hortus_hexis" / "registry.json"


def _load() -> List[Dict]:
    if not REG.exists():
        return []
    try:
        return json.loads(REG.read_text())
    except json.JSONDecodeError:
        return []


def record(name: str, seed: str, content: str, checked: int, commit: str = "") -> Dict:
    entries = _load()
    entry = {
        "ts": time.time(), "name": safe_name(name), "seed": seed,
        "content": content[:120], "checked": bool(checked), "commit": commit,
    }
    entries = [e for e in entries if e["name"] != entry["name"]]
    entries.append(entry)
    REG.parent.mkdir(parents=True, exist_ok=True)
    REG.write_text(json.dumps(entries, indent=2))
    return entry


def all() -> List[Dict]:
    return _load()


def lineage(seed: str) -> List[Dict]:
    return [e for e in _load() if e.get("seed") == seed]
