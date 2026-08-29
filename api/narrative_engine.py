"""Narrative Engine — weaves system events into evolving storylines.

Every event in the system becomes a character, plot point, or setting
in an ongoing narrative. The engine tracks story arcs, identifies
climactic moments, and generates chapter summaries from raw telemetry.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class StoryArc:
    def __init__(self, name: str, genre: str = "cosmic_horror"):
        self.name = name
        self.genre = genre
        self.chapters: List[Dict[str, Any]] = []
        self.characters: List[str] = []
        self.tension = 0.0
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{name}:{self.created_at}".encode()).hexdigest()[:8]

    def add_event(self, event: str, actors: List[str], mood: str = "neutral") -> Dict[str, Any]:
        tension_map = {
            "calm": 0.1, "curious": 0.3, "tense": 0.6,
            "dramatic": 0.8, "catastrophic": 1.0, "triumphant": 0.7,
        }
        chapter_num = len(self.chapters) + 1
        chapter = {
            "chapter": chapter_num,
            "event": event,
            "actors": actors,
            "mood": mood,
            "tension": tension_map.get(mood, 0.5),
            "timestamp": time.time(),
            "narrative": self._generate_narrative(event, actors, mood, chapter_num),
        }
        self.chapters.append(chapter)
        self.tension = chapter["tension"]
        for actor in actors:
            if actor not in self.characters:
                self.characters.append(actor)
        return chapter

    def _generate_narrative(self, event: str, actors: List[str], mood: str, chapter: int) -> str:
        actor_str = " and ".join(actors) if actors else "the void"
        mood_verbs = {
            "calm": "observed",
            "curious": "investigated",
            "tense": "braced against",
            "dramatic": "confronted",
            "catastrophic": "shattered under",
            "triumphant": "celebrated",
        }
        verb = mood_verbs.get(mood, "witnessed")
        return f"Chapter {chapter}: {actor_str} {verb} {event}."

    def climax_detected(self) -> bool:
        if len(self.chapters) < 3:
            return False
        recent = [c["tension"] for c in self.chapters[-3:]]
        return max(recent) > 0.8 and len(self.chapters) > 5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "genre": self.genre,
            "chapters": len(self.chapters),
            "characters": self.characters,
            "tension": round(self.tension, 3),
            "climax_detected": self.climax_detected(),
        }


class NarrativeEngine:
    def __init__(self):
        self.arcs: Dict[str, StoryArc] = {}
        self.event_log: List[Dict[str, Any]] = []

    def create_arc(self, name: str, genre: str = "cosmic_horror") -> Dict[str, Any]:
        arc = StoryArc(name, genre)
        self.arcs[arc.id] = arc
        return {"arc": arc.to_dict()}

    def add_event(self, arc_id: str, event: str, actors: List[str], mood: str = "neutral") -> Dict[str, Any]:
        if arc_id not in self.arcs:
            return {"error": "arc not found"}
        chapter = self.arcs[arc_id].add_event(event, actors, mood)
        self.event_log.append({"arc_id": arc_id, **chapter, "time": time.time()})
        return {"chapter": chapter}

    def get_summary(self, arc_id: str) -> Dict[str, Any]:
        if arc_id not in self.arcs:
            return {"error": "arc not found"}
        arc = self.arcs[arc_id]
        chapters_text = "\n".join(c["narrative"] for c in arc.chapters)
        return {
            "arc": arc.to_dict(),
            "full_narrative": chapters_text,
            "story_so_far": arc.chapters[-3:] if arc.chapters else [],
        }

    def detect_climaxes(self) -> List[Dict[str, Any]]:
        climaxes = []
        for arc in self.arcs.values():
            if arc.climax_detected():
                climaxes.append({"arc": arc.to_dict(), "message": f"CLIMAX in '{arc.name}'"})
        return climaxes

    def engine_stats(self) -> Dict[str, Any]:
        total_chapters = sum(len(a.chapters) for a in self.arcs.values())
        return {
            "total_arcs": len(self.arcs),
            "total_chapters": total_chapters,
            "total_characters": len(set(c for a in self.arcs.values() for c in a.characters)),
            "climaxes_detected": len(self.detect_climaxes()),
        }


_engine = NarrativeEngine()


def narrative_engine_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "create":
        return _engine.create_arc(payload.get("name", "Untitled"), payload.get("genre", "cosmic_horror"))
    elif action == "event":
        return _engine.add_event(
            payload.get("arc_id", ""), payload.get("event", "something happened"),
            payload.get("actors", []), payload.get("mood", "neutral"),
        )
    elif action == "summary":
        return _engine.get_summary(payload.get("arc_id", ""))
    elif action == "climaxes":
        return {"climaxes": _engine.detect_climaxes()}
    return {"status": "active", **_engine.engine_stats()}


handler = narrative_engine_handler
