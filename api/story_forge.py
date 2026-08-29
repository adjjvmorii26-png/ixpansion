"""Story Forge — agents collaboratively write evolving narratives.

Multiple agents contribute to a shared story, each adding characters,
plot twists, and world details. The story evolves organically, with
agents sometimes contradicting each other, creating plot holes that
other agents must resolve. The result is an emergent collaborative fiction.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class StoryElement:
    def __init__(self, author: str, element_type: str, content: str):
        self.author = author
        self.element_type = element_type
        self.content = content
        self.timestamp = time.time()
        self.impact = random.uniform(0.1, 1.0)


class Story:
    def __init__(self, title: str, genre: str = "speculative_fiction"):
        self.title = title
        self.genre = genre
        self.elements: List[StoryElement] = []
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{title}:{self.created_at}".encode()).hexdigest()[:8]

    def add_element(self, author: str, element_type: str, content: str) -> Dict[str, Any]:
        element = StoryElement(author, element_type, content)
        self.elements.append(element)
        if element_type == "character":
            name = content.split()[0] if content else "unknown"
            self.characters[name] = {"name": name, "created_by": author, "alive": True}
        return {
            "type": element_type,
            "author": author,
            "content": content[:60],
            "impact": round(element.impact, 3),
            "total_elements": len(self.elements),
        }

    def narrative_so_far(self) -> str:
        parts = []
        for e in self.elements:
            parts.append(f"[{e.element_type.upper()} by {e.author}]: {e.content}")
        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "genre": self.genre,
            "elements": len(self.elements),
            "characters": len(self.characters),
            "authors": len(set(e.author for e in self.elements)),
        }


class StoryForge:
    def __init__(self):
        self.stories: Dict[str, Story] = []
        self.collaboration_log: List[Dict[str, Any]] = []

    def create_story(self, title: str, genre: str = "speculative_fiction") -> Dict[str, Any]:
        story = Story(title, genre)
        self.stories.append(story)
        return {"story": story.to_dict()}

    def contribute(self, story_id: str, author: str, element_type: str, content: str) -> Dict[str, Any]:
        for story in self.stories:
            if story.id == story_id:
                result = story.add_element(author, element_type, content)
                self.collaboration_log.append({"story": story.title, "author": author, "type": element_type, "time": time.time()})
                return result
        return {"error": "story not found"}

    def read_story(self, story_id: str) -> Dict[str, Any]:
        for story in self.stories:
            if story.id == story_id:
                return {"narrative": story.narrative_so_far(), "meta": story.to_dict()}
        return {"error": "story not found"}

    def story_library(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self.stories]

    def forge_stats(self) -> Dict[str, Any]:
        return {
            "total_stories": len(self.stories),
            "total_contributions": len(self.collaboration_log),
            "total_elements": sum(len(s.elements) for s in self.stories),
            "unique_authors": len(set(c["author"] for c in self.collaboration_log)),
        }


_forge = StoryForge()


def story_forge_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "create":
        return _forge.create_story(payload.get("title", "Untitled"), payload.get("genre", "speculative_fiction"))
    elif action == "contribute":
        return _forge.contribute(
            payload.get("story_id", ""),
            payload.get("author", "anonymous"),
            payload.get("element_type", "plot"),
            payload.get("content", "something happens"),
        )
    elif action == "read":
        return _forge.read_story(payload.get("story_id", ""))
    elif action == "library":
        return {"stories": _forge.story_library()}
    return {"status": "active", **_forge.forge_stats()}


handler = story_forge_handler
