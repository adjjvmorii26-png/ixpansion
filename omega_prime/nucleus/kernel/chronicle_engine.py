"""Chronicle engine — emergent narrative memory.

Observes all system events and compresses them into short "chronicle
entries." Over time these entries accumulate into a cultural record.
New agents can read the chronicles and inherit the accumulated wisdom
(and biases) of previous generations.

Chronicles are NOT logs. They are interpretive summaries that lose
detail but gain meaning through compression — like oral tradition.
"""
from __future__ import annotations

import hashlib
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class EventWeight(Enum):
    TRIVIAL = auto()
    NOTEWORTHY = auto()
    SIGNIFICANT = auto()
    LEGENDARY = auto()


@dataclass
class ChronicleEntry:
    entry_id: str
    tick: int
    epoch: int
    weight: EventWeight
    narrative: str
    actors: list[str]
    tags: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.entry_id,
            "tick": self.tick,
            "epoch": self.epoch,
            "weight": self.weight.name,
            "story": self.narrative,
            "who": self.actors,
            "tags": sorted(self.tags),
        }


class ChronicleEngine:
    def __init__(self) -> None:
        self._entries: list[ChronicleEntry] = []
        self._epoch = 0
        self._epoch_size = 100  # ticks per epoch
        self._tag_index: dict[str, list[str]] = defaultdict(list)
        self._actor_reputation: dict[str, float] = defaultdict(float)

    def _classify(self, event: dict[str, Any]) -> EventWeight:
        intent = event.get("intent", "")
        if intent in ("create_realm", "teleport"):
            return EventWeight.LEGENDARY
        if intent in ("attack", "alert", "construct"):
            return EventWeight.SIGNIFICANT
        if intent in ("move", "patrol", "report"):
            return EventWeight.NOTEWORTHY
        return EventWeight.TRIVIAL

    def _narrate(self, event: dict[str, Any], weight: EventWeight) -> str:
        actor = event.get("actor", "unknown")
        action = event.get("intent", "did something")
        target = event.get("target", "")
        realm = event.get("realm", "")

        templates = {
            EventWeight.TRIVIAL: f"{actor} {action} quietly.",
            EventWeight.NOTEWORTHY: f"{actor} {action}{' toward ' + target if target else ''}.",
            EventWeight.SIGNIFICANT: f"In {realm}, {actor} chose to {action}" +
                                     (f" against {target}" if target else "") + ".",
            EventWeight.LEGENDARY: f"{actor} {action}{' into ' + target if target else ''}" +
                                   f" — the {realm} trembled.",
        }
        return templates[weight]

    def observe(self, tick: int, event: dict[str, Any]) -> ChronicleEntry | None:
        """Observe an event; only noteworthy+ events are recorded."""
        weight = self._classify(event)
        if weight == EventWeight.TRIVIAL:
            return None

        epoch = tick // self._epoch_size
        narrative = self._narrate(event, weight)
        eid = hashlib.sha256(f"{tick}:{narrative}".encode()).hexdigest()[:12]

        actors = [event.get("actor", "unknown")]
        tags = {event.get("intent", ""), event.get("realm", "")} - {""}

        entry = ChronicleEntry(
            entry_id=eid, tick=tick, epoch=epoch,
            weight=weight, narrative=narrative,
            actors=actors, tags=tags,
        )
        self._entries.append(entry)

        for tag in tags:
            self._tag_index[tag].append(eid)
        for actor in actors:
            rep_boost = {"NOTEWORTHY": 0.01, "SIGNIFICANT": 0.05, "LEGENDARY": 0.2}
            self._actor_reputation[actor] += rep_boost.get(weight.name, 0.01)

        return entry

    def recall(self, tags: set[str] | None = None, min_weight: EventWeight = EventWeight.NOTEWORTHY,
               limit: int = 10) -> list[dict[str, Any]]:
        """Query chronicles by tag and minimum significance."""
        results = [
            e for e in reversed(self._entries)
            if e.weight.value >= min_weight.value
            and (not tags or tags & e.tags)
        ]
        return [e.to_dict() for e in results[:limit]]

    def inherit(self, agent_id: str) -> list[dict[str, Any]]:
        """A new agent reads the chronicles for the first time."""
        # New agents get the most significant recent stories as their origin myth
        significant = self.recall(min_weight=EventWeight.SIGNIFICANT, limit=3)
        return significant

    @property
    def reputation(self) -> dict[str, float]:
        return {k: round(v, 4) for k, v in sorted(self._actor_reputation.items(), key=lambda x: -x[1])}

    @property
    def stats(self) -> dict[str, Any]:
        by_weight = defaultdict(int)
        for e in self._entries:
            by_weight[e.weight.name] += 1
        epochs = len(set(e.epoch for e in self._entries))
        return {
            "total_entries": len(self._entries),
            "epochs": epochs,
            "by_weight": dict(by_weight),
            "unique_tags": len(self._tag_index),
        }
