"""Wave 126 — Myth Engine.

Generates myths from system events — transforming mundane occurrences
into epic narratives with heroes, villains, trials, and revelations.
Every commit becomes a legend, every bug becomes a dragon.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class Myth:
    """A generated myth from system events."""

    ARCHETYPES = ["hero", "trickster", "mentor", "shadow", "shapeshifter", "oracle"]

    def __init__(self, title: str, source_event: str):
        self.title = title
        self.source_event = source_event
        self.created = time.time()
        self.chapters: List[str] = []
        self.characters: List[Dict[str, str]] = []
        self.moral: str = ""
        self.id = hashlib.sha256(f"myth:{title}".encode()).hexdigest()[:10]

    def add_chapter(self, chapter: str) -> None:
        self.chapters.append(chapter)

    def add_character(self, name: str, archetype: str = "hero") -> None:
        self.characters.append({"name": name, "archetype": archetype})

    def set_moral(self, moral: str) -> None:
        self.moral = moral

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "title": self.title, "source": self.source_event,
            "chapters": len(self.chapters), "characters": len(self.characters),
            "moral": self.moral,
        }


class MythEngine:
    """Generates myths from system events."""

    def __init__(self):
        self._myths: List[Myth] = []
        self._generation_count = 0

    def generate(self, title: str, source_event: str) -> Myth:
        myth = Myth(title, source_event)
        myth.add_chapter(f"In the beginning, there was '{source_event}'...")
        myth.add_chapter(f"The forces gathered and '{title}' was born.")
        myth.add_character("The Protagonist", "hero")
        myth.add_character("The Obstacle", "shadow")
        myth.set_moral(f"From '{source_event}' we learn perseverance.")
        self._myths.append(myth)
        self._generation_count += 1
        return myth

    def epic_cycle(self, events: List[str]) -> List[Myth]:
        myths = []
        for i, event in enumerate(events):
            myth = self.generate(f"Chapter {i+1}: {event}", event)
            myths.append(myth)
        return myths

    def get_myths(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self._myths]

    def status(self) -> Dict[str, Any]:
        total_chapters = sum(len(m.chapters) for m in self._myths)
        total_characters = sum(len(m.characters) for m in self._myths)
        return {"total_myths": len(self._myths), "total_chapters": total_chapters,
                "total_characters": total_characters, "generations": self._generation_count}
