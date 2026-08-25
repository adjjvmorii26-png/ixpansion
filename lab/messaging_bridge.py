"""Messaging Bridge — Connects event_bus, channels, and linguistic_drift.

Provides a unified messaging layer that supports topic-based pub/sub,
channel routing, and message evolution over time.
"""
from __future__ import annotations
import hashlib
import random
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]


class LinguisticDrift:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.vocabulary: dict[str, float] = {}
        self.drift_log: list[dict] = []

    def register_term(self, term: str, weight: float = 1.0):
        self.vocabulary[term] = weight

    def drift(self, steps: int = 5):
        for _ in range(steps):
            for term in list(self.vocabulary.keys()):
                change = random.Random(abs(hash(term)) % (2**31)).uniform(-0.1, 0.1)
                self.vocabulary[term] = max(0, min(2, self.vocabulary[term] + change))
            self.drift_log.append(dict(self.vocabulary))

    def evolve_term(self, term: str) -> str:
        if term not in self.vocabulary:
            return term
        chars = list(term)
        if len(chars) > 3:
            idx = random.Random(hash(term)).randint(1, len(chars) - 2)
            chars[idx] = random.Random(hash(term + str(idx))).choice("aeiou")
        return "".join(chars)


class MessageChannel:
    def __init__(self, name: str, capacity: int = 100):
        self.name = name
        self.capacity = capacity
        self.buffer: list[dict] = []
        self.subscribers: list[Callable] = []

    def publish(self, message: dict):
        self.buffer.append(message)
        if len(self.buffer) > self.capacity:
            self.buffer = self.buffer[-self.capacity:]
        for sub in self.subscribers:
            try:
                sub(message)
            except Exception:
                pass

    def subscribe(self, callback: Callable):
        self.subscribers.append(callback)

    def get_history(self, count: int = 10) -> list[dict]:
        return self.buffer[-count:]


class MessagingBridge:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.channels: dict[str, MessageChannel] = {}
        self.drift = LinguisticDrift(seed)
        self.message_count = 0
        self.topic_handlers: dict[str, list[Callable]] = defaultdict(list)

    def create_channel(self, name: str, capacity: int = 100) -> MessageChannel:
        channel = MessageChannel(name, capacity)
        self.channels[name] = channel
        return channel

    def on(self, topic: str, handler: Callable):
        self.topic_handlers[topic].append(handler)

    def emit(self, topic: str, data: dict):
        self.message_count += 1
        message = {"topic": topic, "data": data, "timestamp": time.time(), "id": self.message_count}
        for handler in self.topic_handlers.get(topic, []):
            try:
                handler(message)
            except Exception:
                pass
        for channel in self.channels.values():
            channel.publish(message)

    def send_to_channel(self, channel_name: str, data: dict):
        if channel_name in self.channels:
            self.channels[channel_name].publish({
                "data": data, "timestamp": time.time(), "channel": channel_name
            })

    def report(self) -> dict:
        return {
            "bridge": "messaging_bridge",
            "channels": {name: {"buffer_size": len(ch.buffer), "subscribers": len(ch.subscribers)}
                         for name, ch in self.channels.items()},
            "topics": list(self.topic_handlers.keys()),
            "total_messages": self.message_count,
            "drift_terms": len(self.drift.vocabulary),
        }


def demo():
    bridge = MessagingBridge(seed=42)
    bridge.create_channel("agent_events", 50)
    bridge.create_channel("system_alerts", 30)
    agent_log = []
    bridge.on("agent_action", lambda m: agent_log.append(m))
    bridge.emit("agent_action", {"agent": "scout_0", "action": "move"})
    bridge.emit("agent_action", {"agent": "sentinel_0", "action": "alert"})
    bridge.emit("system_event", {"type": "heartbeat", "epoch": 1})
    bridge.send_to_channel("agent_events", {"forward": True})
    bridge.drift.register_term("sentinel")
    bridge.drift.register_term("architect")
    bridge.drift.register_term("wanderer")
    bridge.drift.drift(steps=3)
    return bridge.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
