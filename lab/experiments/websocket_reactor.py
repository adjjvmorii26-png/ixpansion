#!/usr/bin/env python3
"""WebSocket Reactor — real-time event streaming for the dashboard.

Bridges the lab experiments with the Vercel dashboard by creating
a lightweight event streaming protocol. Experiments push events
to the reactor, which buffers and batches them for efficient
delivery to connected dashboard clients.

Events are typed: observation, mutation, alert, heartbeat.
The reactor tracks event rates and can trigger alerts when
rates exceed thresholds.
"""
from __future__ import annotations

import hashlib
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StreamEvent:
    event_id: str
    event_type: str
    source: str
    payload: dict[str, Any]
    timestamp: float
    sequence: int

    def to_json(self) -> str:
        return json.dumps({
            "id": self.event_id,
            "type": self.event_type,
            "source": self.source,
            "payload": self.payload,
            "ts": self.timestamp,
            "seq": self.sequence,
        })


@dataclass
class StreamClient:
    client_id: str
    subscribed_types: set[str]
    last_seen_seq: int = 0
    connected_at: float = 0.0
    events_received: int = 0


@dataclass
class WebSocketReactor:
    """Real-time event streaming for dashboard connectivity."""
    buffer_size: int = 100
    rate_threshold: float = 10.0
    alert_window: float = 5.0
    seed: int | None = None

    def __post_init__(self) -> None:
        self._buffer: list[StreamEvent] = []
        self._clients: dict[str, StreamClient] = {}
        self._sequence = 0
        self._event_rates: dict[str, list[float]] = defaultdict(list)
        self._alerts: list[dict[str, Any]] = []
        self._tick = 0

    def push_event(self, event_type: str, source: str,
                   payload: dict[str, Any] | None = None) -> StreamEvent:
        self._sequence += 1
        now = time.time()
        event = StreamEvent(
            event_id=hashlib.sha256(
                f"{source}:{event_type}:{self._sequence}".encode()
            ).hexdigest()[:12],
            event_type=event_type,
            source=source,
            payload=payload or {},
            timestamp=now,
            sequence=self._sequence,
        )
        self._buffer.append(event)
        if len(self._buffer) > self.buffer_size:
            self._buffer = self._buffer[-self.buffer_size:]

        # Track rates
        self._event_rates[event_type].append(now)
        self._event_rates[event_type] = [
            t for t in self._event_rates[event_type]
            if now - t < self.alert_window
        ]

        # Check rate threshold
        rate = len(self._event_rates[event_type]) / self.alert_window
        if rate > self.rate_threshold:
            alert = {
                "type": "rate_exceeded",
                "event_type": event_type,
                "rate": round(rate, 2),
                "threshold": self.rate_threshold,
                "timestamp": now,
            }
            self._alerts.append(alert)

        return event

    def subscribe(self, client_id: str, event_types: list[str]) -> StreamClient:
        client = StreamClient(
            client_id=client_id,
            subscribed_types=set(event_types),
            connected_at=time.time(),
        )
        self._clients[client_id] = client
        return client

    def poll(self, client_id: str, max_events: int = 10) -> list[dict[str, Any]]:
        client = self._clients.get(client_id)
        if not client:
            return []

        events = [
            e for e in self._buffer
            if e.sequence > client.last_seen_seq
            and (not client.subscribed_types or e.event_type in client.subscribed_types)
        ][:max_events]

        if events:
            client.last_seen_seq = events[-1].sequence
            client.events_received += len(events)

        return [json.loads(e.to_json()) for e in events]

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        # Heartbeat
        self.push_event("heartbeat", "reactor", {"tick": self._tick})
        return {"tick": self._tick, "buffer_size": len(self._buffer)}

    def reactor_status(self) -> dict[str, Any]:
        now = time.time()
        rates = {}
        for etype, timestamps in self._event_rates.items():
            recent = [t for t in timestamps if now - t < self.alert_window]
            rates[etype] = round(len(recent) / self.alert_window, 2)

        return {
            "tick": self._tick,
            "buffer_size": len(self._buffer),
            "sequence": self._sequence,
            "clients": len(self._clients),
            "event_rates": rates,
            "alerts": len(self._alerts),
            "recent_alerts": self._alerts[-3:],
        }


def demo() -> dict[str, Any]:
    reactor = WebSocketReactor(seed=42)

    # Register a client
    reactor.subscribe("dashboard-1", ["observation", "mutation", "alert"])

    # Simulate event streams
    sources = ["spectral_drift", "cross_pollinator", "memory_palace"]
    for tick in range(20):
        reactor.tick()
        for source in sources:
            reactor.push_event("observation", source, {"tick": tick, "value": tick * 0.1})
            if tick % 5 == 0:
                reactor.push_event("mutation", source, {"change": "entropy_shift"})

    # Client polls
    events = reactor.poll("dashboard-1", max_events=5)

    return {
        "status": reactor.reactor_status(),
        "sample_events": events,
    }


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
