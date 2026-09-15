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


def handler(req: dict = None, context: dict = None) -> dict:
    """Handle event stream requests."""
    req = req or {}
    action = req.get("action", "stream")

    if action == "stream":
        return {
            "action": "stream",
            "channels": sorted({e["type"].split(".")[0] for e in EVENT_LOG}),
            "subscriptions": len(SUBSCRIBERS),
            "events": EVENT_LOG[-20:],
        }

    elif action == "recent":
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

    elif action == "channels":
        channels = sorted({e["type"].split(".")[0] for e in EVENT_LOG})
        return {"action": "channels", "channels": channels}

    elif action == "subscriptions":
        return {"action": "subscriptions", "subscriptions": [], "active": len(SUBSCRIBERS)}

    return {"error": "use action=recent|emit|stats|channels|subscriptions"}


def coherence_vitals() -> dict:
    return {"organ": "event_stream", "status": "active", "events": len(EVENT_LOG)}


class EventStream:
    """Full pub/sub event stream for the organism.

    Exposes the tested contract: publish, subscribe, stream, channels,
    and set_filter. Pattern matching uses fnmatch wildcards (e.g.
    ``agent.*`` matches ``agent.lifecycle``), and filters narrow results
    by the event payload's ``event`` field.
    """

    def __init__(self):
        self.subscriptions: dict[str, dict] = {}
        self.buffer: list[dict] = []
        self.channel_names: set[str] = set()
        self._sub_counter = 0
        self._event_counter = 0

    def publish(self, event_type: str, data: dict, priority: str = "normal") -> dict:
        """Publish an event to the stream. Returns event_id + priority."""
        self._event_counter += 1
        event = {
            "event_id": f"evt_{self._event_counter}",
            "type": event_type,
            "data": data,
            "priority": priority,
            "timestamp": time.time(),
        }
        self.buffer.append(event)
        self.channel_names.add(event_type.split(".")[0])
        # Also broadcast through the module-level event bus for live SSE.
        try:
            emit_event(event_type, event_type.split(".")[0], data)
        except Exception:
            pass
        return {"event_id": event["event_id"], "priority": priority}

    def subscribe(self, user_id: str, pattern: str) -> dict:
        """Subscribe a user to an event pattern. Returns subscription_id."""
        self._sub_counter += 1
        sid = f"sub_{self._sub_counter}_{user_id}"
        self.subscriptions[sid] = {"user": user_id, "pattern": pattern, "filters": []}
        return {"subscription_id": sid}

    def set_filter(self, subscription_id: str, filters: list) -> dict:
        """Restrict a subscription to specific event payload values."""
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id]["filters"] = list(filters)
            return {"ok": True, "subscription_id": subscription_id, "filters": list(filters)}
        return {"error": "subscription not found"}

    def stream(self, subscription_id: str) -> list:
        """Return buffered events matching the subscription's pattern/filter."""
        sub = self.subscriptions.get(subscription_id)
        if not sub:
            return []
        import fnmatch
        events = [e for e in self.buffer if fnmatch.fnmatch(e["type"], sub["pattern"])]
        if sub["filters"]:
            events = [e for e in events if e.get("data", {}).get("event") in sub["filters"]]
        return events

    def channels(self) -> list:
        """All channel names seen by this stream instance."""
        return sorted(self.channel_names)

def resonates_with():
    return ['organism_core', 'coherence_validator', 'consensus_bloom', 'council_oracle', 'causality_weave']

