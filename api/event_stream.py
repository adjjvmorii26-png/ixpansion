"""SSE Event Stream — live organism state updates.

Usage:
    GET /api/events          — SSE stream of organism events
    GET /api/events?filter=wave432 — filter by module
    GET /api/events?since=<timestamp> — events since timestamp
"""
from __future__ import annotations
import json
import time
import queue
import threading
from pathlib import Path

EVENT_LOG: list[dict] = []
SUBSCRIBERS: list[queue.Queue] = []
MAX_LOG = 200


def emit_event(event_type: str, module: str, data: dict) -> None:
    """Emit an event to all subscribers."""
    event = {
        "id": len(EVENT_LOG),
        "type": event_type,
        "module": module,
        "data": data,
        "timestamp": time.time(),
    }
    EVENT_LOG.append(event)
    if len(EVENT_LOG) > MAX_LOG:
        EVENT_LOG.pop(0)
    dead = []
    for q in SUBSCRIBERS:
        try:
            q.put_nowait(event)
        except queue.Full:
            dead.append(q)
    for q in dead:
        SUBSCRIBERS.remove(q)


def handler(req: dict = None) -> dict:
    """Handle event stream requests."""
    req = req or {}
    action = req.get("action", "stream")

    if action == "recent":
        count = req.get("count", 20)
        since = req.get("since", 0)
        events = [e for e in EVENT_LOG if e["timestamp"] > since]
        filter_mod = req.get("filter")
        if filter_mod:
            events = [e for e in events if filter_mod in e["module"]]
        return {
            "action": "recent",
            "events": events[-count:],
            "total": len(EVENT_LOG),
        }

    elif action == "emit":
        emit_event(
            req.get("type", "manual"),
            req.get("module", "system"),
            req.get("data", {}),
        )
        return {"action": "emit", "ok": True}

    elif action == "stats":
        modules = {}
        for e in EVENT_LOG:
            modules[e["module"]] = modules.get(e["module"], 0) + 1
        return {
            "action": "stats",
            "total_events": len(EVENT_LOG),
            "subscribers": len(SUBSCRIBERS),
            "modules": modules,
        }

    return {"error": "use action=recent|emit|stats"}


def coherence_vitals() -> dict:
    return {"organ": "event_stream", "status": "active", "events": len(EVENT_LOG)}
