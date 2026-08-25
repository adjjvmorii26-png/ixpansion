"""Streaming Reactor — Real-time event stream with history and replay.

Maintains an event buffer, supports subscriber patterns, and can replay
historical events for debugging and analysis.
"""
from __future__ import annotations
import hashlib
import time
from collections import deque
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]


class ReactorEvent:
    """A single event in the reactor stream."""

    def __init__(self, event_type: str, source: str, payload: dict, priority: int = 0):
        self.event_type = event_type
        self.source = source
        self.payload = payload
        self.priority = priority
        self.timestamp = time.time()
        self.event_id = hashlib.md5(
            f"{event_type}:{source}:{self.timestamp}".encode()
        ).hexdigest()[:12]

    def to_dict(self) -> dict:
        return {
            "id": self.event_id,
            "type": self.event_type,
            "source": self.source,
            "payload": self.payload,
            "priority": self.priority,
            "timestamp": self.timestamp,
        }


class Subscriber:
    """A subscriber to specific event types."""

    def __init__(self, name: str, event_types: list[str], callback: Callable):
        self.name = name
        self.event_types = set(event_types)
        self.callback = callback
        self.received: list[ReactorEvent] = []
        self.active = True

    def matches(self, event: ReactorEvent) -> bool:
        return "*" in self.event_types or event.event_type in self.event_types

    def receive(self, event: ReactorEvent):
        if self.matches(event) and self.active:
            self.received.append(event)
            self.callback(event)


class StreamingReactor:
    """Event-driven reactor with streaming capabilities."""

    def __init__(self, buffer_size: int = 1000, seed: int = 42):
        self.buffer_size = buffer_size
        self.seed = seed
        self.events: deque[ReactorEvent] = deque(maxlen=buffer_size)
        self.subscribers: dict[str, Subscriber] = {}
        self.total_published = 0
        self.total_delivered = 0
        self.event_types_seen: set[str] = set()

    def publish(self, event_type: str, source: str, payload: dict, priority: int = 0) -> ReactorEvent:
        event = ReactorEvent(event_type, source, payload, priority)
        self.events.append(event)
        self.total_published += 1
        self.event_types_seen.add(event_type)

        # Deliver to subscribers
        for sub in self.subscribers.values():
            if sub.matches(event):
                sub.receive(event)
                self.total_delivered += 1

        return event

    def subscribe(self, name: str, event_types: list[str], callback: Callable | None = None):
        if callback is None:
            callback = lambda e: None
        self.subscribers[name] = Subscriber(name, event_types, callback)

    def unsubscribe(self, name: str):
        self.subscribers.pop(name, None)

    def replay(self, start_time: float | None = None, end_time: float | None = None,
               event_type: str | None = None) -> list[dict]:
        """Replay events from the buffer with optional filters."""
        result = []
        for event in self.events:
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            if event_type and event.event_type != event_type:
                continue
            result.append(event.to_dict())
        return result

    def get_recent(self, count: int = 10) -> list[dict]:
        """Get the most recent events."""
        events_list = list(self.events)
        return [e.to_dict() for e in events_list[-count:]]

    def stats(self) -> dict:
        """Get reactor statistics."""
        type_counts = {}
        for event in self.events:
            type_counts[event.event_type] = type_counts.get(event.event_type, 0) + 1

        return {
            "buffer_size": len(self.events),
            "max_buffer": self.buffer_size,
            "total_published": self.total_published,
            "total_delivered": self.total_delivered,
            "subscriber_count": len(self.subscribers),
            "event_types": sorted(self.event_types_seen),
            "type_distribution": type_counts,
        }

    def report(self) -> dict:
        return {
            "reactor": "streaming_reactor",
            "stats": self.stats(),
            "recent_events": self.get_recent(5),
            "subscribers": {
                name: {"event_types": sorted(sub.event_types), "received": len(sub.received)}
                for name, sub in self.subscribers.items()
            },
        }


def demo():
    reactor = StreamingReactor(buffer_size=500, seed=42)

    # Register subscribers
    reactor.subscribe("monitor", ["*"])
    reactor.subscribe("alert_system", ["error", "warning"])
    reactor.subscribe("logger", ["agent_action", "realm_event"])

    # Simulate event stream
    event_types = [
        ("agent_action", "sandbox", {"action": "move", "agent": "scout_0"}),
        ("realm_event", "sandbox", {"epoch": 1, "agents": 5}),
        ("signal", "bridge", {"source": "omega_prime", "target": "omega_fractal"}),
        ("error", "vm", {"opcode": "INVALID", "line": 42}),
        ("warning", "fossil_registry", {"type": "empty_function", "file": "test.py"}),
        ("agent_action", "sandbox", {"action": "build", "agent": "builder_0"}),
        ("heartbeat", "engine", {"alive": True, "epoch": 10}),
        ("mutation", "mutation_network", {"from": "module_a", "to": "module_b"}),
    ]

    for i, (etype, source, payload) in enumerate(event_types):
        reactor.publish(etype, source, payload, priority=i % 3)

    return reactor.report()


def main():
    import json
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
