from __future__ import annotations
"""Chronicle Loom — weaves a chronological tapestry of system events.

Like a loom weaving threads into fabric, this module interlaces event
streams from multiple subsystems into a unified chronological tapestry.
Each thread represents a different subsystem; crossings represent
interactions. The resulting pattern reveals the hidden structure of
system behavior over time.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

class ThreadColor(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    GOLD = "gold"
    VIOLET = "violet"
    SILVER = "silver"

@dataclass
class Event:
    timestamp: float
    subsystem: str
    event_type: str
    detail: str = ""
    thread_color: ThreadColor = ThreadColor.SILVER
    intensity: float = 1.0

@dataclass
class Crossing:
    timestamp: float
    thread_a: str
    thread_b: str
    event_a: Event
    event_b: Event
    significance: float = 0.0

@dataclass
class Tapestry:
    events: List[Event]
    crossings: List[Crossing]
    pattern_hash: str
    weave_complexity: float
    thread_count: int
    timespan: Tuple[float, float]

class ChronicleLoom:
    THREAD_COLORS = {
        "nucleus": ThreadColor.GOLD,
        "agents": ThreadColor.RED,
        "sandbox": ThreadColor.BLUE,
        "protocols": ThreadColor.GREEN,
        "experiments": ThreadColor.VIOLET,
        "meta": ThreadColor.SILVER,
    }

    def __init__(self):
        self.events: List[Event] = []
        self.crossings: List[Crossing] = []
        self.tick = 0

    def _assign_color(self, subsystem: str) -> ThreadColor:
        for key, color in self.THREAD_COLORS.items():
            if key in subsystem.lower():
                return color
        return ThreadColor.SILVER

    def record_event(self, subsystem: str, event_type: str,
                     detail: str = "", intensity: float = 1.0) -> Event:
        color = self._assign_color(subsystem)
        event = Event(
            timestamp=self.tick,
            subsystem=subsystem,
            event_type=event_type,
            detail=detail,
            thread_color=color,
            intensity=intensity,
        )
        self.events.append(event)
        self.tick += 1
        return event

    def _detect_crossings(self):
        self.crossings.clear()
        events_by_subsystem: Dict[str, List[Event]] = {}
        for e in self.events:
            events_by_subsystem.setdefault(e.subsystem, []).append(e)

        subsystems = list(events_by_subsystem.keys())
        for i, sa in enumerate(subsystems):
            for sb in subsystems[i + 1:]:
                for ea in events_by_subsystem[sa]:
                    for eb in events_by_subsystem[sb]:
                        if abs(ea.timestamp - eb.timestamp) < 2:
                            significance = (ea.intensity + eb.intensity) / 2
                            self.crossings.append(Crossing(
                                timestamp=(ea.timestamp + eb.timestamp) / 2,
                                thread_a=sa, thread_b=sb,
                                event_a=ea, event_b=eb,
                                significance=significance,
                            ))

    def weave(self) -> Tapestry:
        self._detect_crossings()
        pattern_raw = json.dumps([
            {"t": e.timestamp, "s": e.subsystem, "e": e.event_type}
            for e in self.events
        ], sort_keys=True)
        pattern_hash = hashlib.sha256(pattern_raw.encode()).hexdigest()[:16]

        threads = set(e.subsystem for e in self.events)
        timespan = (
            self.events[0].timestamp if self.events else 0,
            self.events[-1].timestamp if self.events else 0,
        )
        complexity = len(self.crossings) / max(len(self.events), 1)

        return Tapestry(
            events=self.events, crossings=self.crossings,
            pattern_hash=pattern_hash, weave_complexity=complexity,
            thread_count=len(threads), timespan=timespan,
        )

    def pattern_analysis(self) -> Dict:
        by_subsystem = {}
        for e in self.events:
            by_subsystem.setdefault(e.subsystem, []).append(e)

        return {
            "total_events": len(self.events),
            "total_crossings": len(self.crossings),
            "threads": list(by_subsystem.keys()),
            "events_per_thread": {k: len(v) for k, v in by_subsystem.items()},
            "high_significance_crossings": [
                {"a": c.thread_a, "b": c.thread_b,
                 "significance": round(c.significance, 3)}
                for c in sorted(self.crossings, key=lambda c: c.significance, reverse=True)[:5]
            ],
        }


def demo():
    loom = ChronicleLoom()
    print("=== Chronicle Loom ===")

    events_data = [
        ("nucleus", "heartbeat", "pulse_tick"),
        ("agents", "spawn", "scout_agent_born"),
        ("sandbox", "tick", "world_advanced"),
        ("nucleus", "heartbeat", "pulse_tick"),
        ("protocols", "message", "hex_encoded"),
        ("agents", "action", "scout_observes"),
        ("sandbox", "event", "collision_detected"),
        ("experiments", "result", "photon_stored"),
        ("nucleus", "heartbeat", "pulse_tick"),
        ("meta", "observation", "pattern_detected"),
        ("agents", "spawn", "analyst_born"),
        ("sandbox", "tick", "world_advanced"),
        ("protocols", "message", "delta_translated"),
        ("nucleus", "heartbeat", "pulse_tick"),
        ("experiments", "result", "crystal_grown"),
    ]
    for subsystem, etype, detail in events_data:
        loom.record_event(subsystem, etype, detail)

    tapestry = loom.weave()
    print(f"  Events woven: {len(tapestry.events)}")
    print(f"  Crossings: {len(tapestry.crossings)}")
    print(f"  Threads: {tapestry.thread_count}")
    print(f"  Pattern hash: {tapestry.pattern_hash}")
    print(f"  Complexity: {tapestry.weave_complexity:.3f}")

    analysis = loom.pattern_analysis()
    print(f"\nEvents per thread:")
    for thread, count in analysis["events_per_thread"].items():
        print(f"  {thread}: {count}")

    print(f"\nHigh-significance crossings:")
    for c in analysis["high_significance_crossings"][:3]:
        print(f"  {c['a']} <-> {c['b']}: significance={c['significance']}")

    return analysis


if __name__ == "__main__":
    demo()
