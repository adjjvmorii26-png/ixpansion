#!/usr/bin/env python3
"""Chronicle Engine Simulator — timeline event recording and analysis.

Bridges chronicle_engine + echo_index + pulse_harmonics to create a
comprehensive event recording system. Events are recorded with
timestamps, source, category, and importance. The engine detects:
- Event clusters (many events in short time)
- Silence periods (no events)
- Echo patterns (events that repeat later)
- Chronicle integrity (hash chain verification)
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ChronicleEvent:
    event_id: str
    tick: int
    source: str
    category: str
    importance: float
    payload: dict[str, Any] = field(default_factory=dict)
    previous_hash: str = ""

    @property
    def event_hash(self) -> str:
        raw = json.dumps({
            "id": self.event_id, "tick": self.tick,
            "source": self.source, "category": self.category,
        }, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass
class ChronicleEngineSim:
    """Comprehensive event recording and analysis."""
    window_size: int = 5
    cluster_threshold: int = 3
    echo_window: int = 20
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = __import__("random").Random(self.seed)
        self._events: list[ChronicleEvent] = []
        self._category_index: dict[str, list[int]] = defaultdict(list)
        self._source_index: dict[str, list[int]] = defaultdict(list)
        self._tick = 0

    def record(self, source: str, category: str, importance: float = 0.5,
               payload: dict[str, Any] | None = None) -> ChronicleEvent:
        self._tick += 1
        prev_hash = self._events[-1].event_hash if self._events else "0" * 16
        event = ChronicleEvent(
            event_id=hashlib.sha256(
                f"{source}:{category}:{self._tick}".encode()
            ).hexdigest()[:12],
            tick=self._tick,
            source=source,
            category=category,
            importance=importance,
            payload=payload or {},
            previous_hash=prev_hash,
        )
        self._events.append(event)
        self._category_index[category].append(self._tick)
        self._source_index[source].append(self._tick)
        return event

    def verify_chain(self) -> dict[str, Any]:
        """Verify the hash chain integrity."""
        broken = []
        for i in range(1, len(self._events)):
            if self._events[i].previous_hash != self._events[i - 1].event_hash:
                broken.append(i)
        return {
            "total_events": len(self._events),
            "chain_valid": len(broken) == 0,
            "broken_links": broken,
        }

    def detect_clusters(self) -> list[dict[str, Any]]:
        """Find periods of high event density."""
        if len(self._events) < self.window_size:
            return []

        clusters: list[dict[str, Any]] = []
        for i in range(len(self._events) - self.window_size + 1):
            window = self._events[i:i + self.window_size]
            ticks = [e.tick for e in window]
            span = max(ticks) - min(ticks)
            if span > 0 and len(window) / span > self.cluster_threshold / 10:
                avg_importance = sum(e.importance for e in window) / len(window)
                clusters.append({
                    "start_tick": window[0].tick,
                    "end_tick": window[-1].tick,
                    "events": len(window),
                    "span": span,
                    "avg_importance": round(avg_importance, 3),
                    "categories": list(set(e.category for e in window)),
                })

        return clusters[:5]

    def detect_echoes(self) -> list[dict[str, Any]]:
        """Find events that repeat later (echoes)."""
        echoes: list[dict[str, Any]] = []
        for i, event_a in enumerate(self._events):
            for j in range(i + 1, min(i + self.echo_window, len(self._events))):
                event_b = self._events[j]
                if (event_a.source == event_b.source
                        and event_a.category == event_b.category):
                    echoes.append({
                        "original_tick": event_a.tick,
                        "echo_tick": event_b.tick,
                        "delay": event_b.tick - event_a.tick,
                        "source": event_a.source,
                        "category": event_a.category,
                    })
                    break
        return echoes[:5]

    def find_silences(self, min_gap: int = 5) -> list[dict[str, Any]]:
        """Find periods with no events."""
        silences: list[dict[str, Any]] = []
        for i in range(1, len(self._events)):
            gap = self._events[i].tick - self._events[i - 1].tick
            if gap >= min_gap:
                silences.append({
                    "from_tick": self._events[i - 1].tick,
                    "to_tick": self._events[i].tick,
                    "gap": gap,
                })
        return silences

    def category_summary(self) -> dict[str, Any]:
        cats = defaultdict(lambda: {"count": 0, "avg_importance": 0.0})
        for e in self._events:
            cats[e.category]["count"] += 1
            cats[e.category]["avg_importance"] += e.importance
        for cat in cats:
            cats[cat]["avg_importance"] = round(
                cats[cat]["avg_importance"] / cats[cat]["count"], 3
            )
        return dict(cats)

    def full_report(self) -> dict[str, Any]:
        return {
            "total_events": len(self._events),
            "chain": self.verify_chain(),
            "clusters": self.detect_clusters(),
            "echoes": self.detect_echoes(),
            "silences": self.find_silences(),
            "categories": self.category_summary(),
        }


def demo() -> dict[str, Any]:
    engine = ChronicleEngineSim(seed=42)
    sources = ["heartbeat", "mycelium", "constellation", "ixpansion"]
    categories = ["pulse", "signal", "mutation", "repair", "observation"]

    for tick in range(50):
        # Normal activity
        engine.record(
            source=sources[tick % len(sources)],
            category=categories[tick % len(categories)],
            importance=engine._rng.uniform(0.2, 0.8),
        )
        # Cluster at tick 20-25
        if 20 <= tick <= 25:
            for _ in range(3):
                engine.record(
                    source="heartbeat",
                    category="pulse",
                    importance=engine._rng.uniform(0.7, 1.0),
                )

    return engine.full_report()


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
