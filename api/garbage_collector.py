"""Wave 140 — Garbage Collector.

Prunes stale runtime data: expired snapshots, orphaned temp files,
and oversized append-logs. Keeps `.runtime/` bounded so durable state
doesn't bloat serverless storage over time.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"


class GarbageCollector:
    """Bounded and prunes accumulated runtime artifacts."""

    def __init__(self, max_snapshots: int = 20, max_log_bytes: int = 5_000_000):
        self.max_snapshots = max_snapshots
        self.max_log_bytes = max_log_bytes

    def cleanup(self) -> Dict[str, int]:
        removed_tmp = 0
        removed_snapshots = 0
        removed_oversized = 0

        # Remove temp files
        if RUNTIME.exists():
            for tmp in RUNTIME.glob("*.tmp"):
                try:
                    tmp.unlink()
                    removed_tmp += 1
                except OSError:
                    pass

        # Trim snapshots beyond max
        snap_dir = RUNTIME / "snapshots"
        if snap_dir.exists():
            snaps = sorted(snap_dir.glob("snapshot-*.json"),
                           key=lambda p: p.stat().st_mtime, reverse=True)
            for stale in snaps[self.max_snapshots:]:
                try:
                    stale.unlink()
                    removed_snapshots += 1
                except OSError:
                    pass

        # Trim oversized append-logs
        if RUNTIME.exists():
            for path in RUNTIME.glob("*.json"):
                try:
                    if path.stat().st_size > self.max_log_bytes:
                        path.unlink()
                        removed_oversized += 1
                except OSError:
                    pass

        return {"tmp": removed_tmp, "snapshots": removed_snapshots,
                "oversized": removed_oversized}

    def status(self) -> Dict[str, Any]:
        return {"max_snapshots": self.max_snapshots,
                "max_log_bytes": self.max_log_bytes}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    gc = GarbageCollector()
    return {"status": "active", "module": "garbage_collector", **gc.status()}
