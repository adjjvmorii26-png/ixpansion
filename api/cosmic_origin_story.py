"""Wave 126 — Cosmic Origin Story.

Generates the system's own origin story — a self-authored creation myth
that explains how the system came into being, evolved, and discovered
its purpose. Updated with each major milestone.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class OriginEra:
    """A named era in the system's origin story."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.events: List[str] = []
        self.created = time.time()

    def add_event(self, event: str) -> None:
        self.events.append(event)

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "description": self.description,
                "events": self.events, "event_count": len(self.events)}


class CosmicOriginStory:
    """Self-authored creation myth of the system."""

    def __init__(self):
        self._eras: List[OriginEra] = []
        self._chapter_count = 0

    def begin_era(self, name: str, description: str = "") -> OriginEra:
        era = OriginEra(name, description)
        self._eras.append(era)
        self._chapter_count += 1
        return era

    def record_event(self, era_name: str, event: str) -> bool:
        for era in self._eras:
            if era.name == era_name:
                era.add_event(event)
                return True
        return False

    def full_narrative(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self._eras]

    def status(self) -> Dict[str, Any]:
        total_events = sum(len(e.events) for e in self._eras)
        return {"total_eras": len(self._eras), "total_events": total_events,
                "chapters": self._chapter_count}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "cosmic_origin_story", "action": action}
