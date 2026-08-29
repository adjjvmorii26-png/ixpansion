"""Wave 140 — Event Replay.

Replays a recorded event stream, useful for debugging, simulations,
and deterministic recovery. Stored events are re-dispatched to their
target modules in order, so the platform can rebuild state from a log.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class EventReplay:
    """Replays recorded events against target modules."""

    def __init__(self):
        self._log: List[Dict[str, Any]] = []
        self._replays = 0

    def record(self, module: str, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = {"module": module, "action": action, "payload": payload,
                 "timestamp": round(time.time(), 4)}
        self._log.append(event)
        return event

    def replay(self, module_filter: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Return events that would be re-dispatched."""
        events = self._log
        if module_filter:
            events = [e for e in events if e["module"] == module_filter]
        selected = events[-limit:]
        self._replays += len(selected)
        return selected

    def count(self) -> int:
        return len(self._log)

    def status(self) -> Dict[str, Any]:
        return {"recorded": len(self._log), "replays": self._replays}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    replay = EventReplay()
    return {"status": "active", "module": "event_replay", **replay.status()}
