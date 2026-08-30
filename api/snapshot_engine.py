"""Wave 140 — Snapshot Engine.

Captures point-in-time snapshots of the entire runtime state into a
single versioned archive under `.runtime/snapshots/`. Snapshots can
be restored to roll the platform back to a known-good state.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
SNAPSHOT_DIR = RUNTIME / "snapshots"


class SnapshotEngine:
    """Creates and restores versioned runtime snapshots."""

    def __init__(self):
        self._snapshots: List[Dict[str, Any]] = []

    def _scan(self) -> List[Path]:
        if not SNAPSHOT_DIR.exists():
            return []
        return sorted(SNAPSHOT_DIR.glob("snapshot-*.json"))

    def capture(self, version: str = "3.59.0") -> Dict[str, Any]:
        data = {}
        if RUNTIME.exists():
            for path in RUNTIME.glob("*.json"):
                try:
                    data[path.stem] = json.loads(path.read_text())
                except (OSError, json.JSONDecodeError):
                    continue
        snapshot = {"version": version, "timestamp": round(time.time(), 4),
                    "namespaces": len(data), "data": data}
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        name = f"snapshot-{time.strftime('%Y%m%d-%H%M%S')}.json"
        (SNAPSHOT_DIR / name).write_text(json.dumps(snapshot, indent=2))
        return {"snapshot": name, "namespaces": len(data)}

    def restore(self, snapshot_name: str) -> Dict[str, Any]:
        path = SNAPSHOT_DIR / snapshot_name
        if not path.exists():
            return {"error": "snapshot not found"}
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            return {"error": "unreadable snapshot"}
        restored = 0
        try:
            import state_store
            for namespace, value in data.get("data", {}).items():
                state_store.write(namespace, value)
                restored += 1
        except ImportError:  # pragma: no cover
            pass
        return {"restored": restored}

    def status(self) -> Dict[str, Any]:
        self._snapshots = [p.name for p in self._scan()]
        return {"snapshots": len(self._snapshots), "names": self._snapshots}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    engine = SnapshotEngine()
    return {"status": "active", "module": "snapshot_engine", **engine.status()}
