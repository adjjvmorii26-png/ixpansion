from __future__ import annotations
"""Interstice bridge enactor — enacts bridges between previously untouched island pairs."""
import json
import time
from pathlib import Path
from typing import Any, Dict, List

_INTERSTICE_PATH = Path(__file__).resolve().parent.parent / "data" / "interstice_bridges.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Enact interstice bridges."""
    bridges = _load_bridges()
    if payload and "island_a" in payload and "island_b" in payload:
        bridge_entry = {
            "island_a": payload["island_a"],
            "island_b": payload["island_b"],
            "enacted": time.time(),
            "stone_count": payload.get("stone_count", 1),
            "meta": payload.get("meta", "new_connection")
        }
        bridges.append(bridge_entry)
        _save_bridges(bridges)
    return {"total_bridges": len(bridges), "latest": bridge_entry if bridges else None}

def _load_bridges() -> List[Dict[str, Any]]:
    try:
        return json.load(open(_INTERSTICE_PATH, encoding="utf-8"))
    except Exception:
        return []

def _save_bridges(bridges: List[Dict[str, Any]]) -> None:
    _INTERSTICE_PATH.write_text(json.dumps(bridges, indent=2, ensure_ascii=False))
