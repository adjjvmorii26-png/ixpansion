"""Wave 132 — Worker Narrative.

Every worker carries a personal narrative: memories of tasks,
relationships, and defining moments. Narratives are searchable and
shape how workers are paired for collaboration.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class NarrativeChapter:
    """A chapter in a worker's life story."""

    def __init__(self, title: str, body: str, mood: str = "neutral"):
        self.title = title
        self.body = body
        self.mood = mood
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"ns:{title}".encode()).hexdigest()[:10]

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "title": self.title, "body": self.body,
                "mood": self.mood, "timestamp": round(self.timestamp, 4)}


class WorkerNarrative:
    """Factory and index of worker life stories."""

    def __init__(self):
        self._stories: Dict[str, List[NarrativeChapter]] = {}
        self._mood_index: Dict[str, int] = {}

    def add(self, worker: str, title: str, body: str, mood: str = "neutral") -> NarrativeChapter:
        chapter = NarrativeChapter(title, body, mood)
        self._stories.setdefault(worker, []).append(chapter)
        self._mood_index[mood] = self._mood_index.get(mood, 0) + 1
        return chapter

    def story(self, worker: str) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self._stories.get(worker, [])]

    def workers(self) -> List[str]:
        return sorted(self._stories)

    def shared_mood(self, worker_a: str, worker_b: str) -> int:
        """Count of moods shared between two workers' narratives."""
        moods_a = {c.mood for c in self._stories.get(worker_a, [])}
        moods_b = {c.mood for c in self._stories.get(worker_b, [])}
        return len(moods_a & moods_b)

    def status(self) -> Dict[str, Any]:
        return {"workers": len(self._stories),
                "chapters": sum(len(v) for v in self._stories.values()),
                "moods": dict(self._mood_index)}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    narrative = WorkerNarrative()
    return {"status": "active", "module": "worker_narrative",
            **narrative.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "protocol", "status": "active", "wave": "132", "module": "worker_narrative"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
