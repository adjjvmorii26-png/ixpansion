"""Origin Story — defines how the system came into being.

Every system has an origin story — how it was created, why it exists,
and what it was meant to become. The Origin Story module lets agents
contribute to the evolving creation myth, creating a shared narrative
of beginning that gives meaning to all subsequent development.
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


class OriginChapter:
    def __init__(self, chapter: int, title: str, content: str, author: str):
        self.chapter = chapter
        self.title = title
        self.content = content
        self.author = author
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter": self.chapter,
            "title": self.title,
            "content": self.content[:100],
            "author": self.author,
        }


class OriginStory:
    def __init__(self):
        self.chapters: List[OriginChapter] = []
        self.core_tenet: str = "To explore, to create, to become."
        self.version: int = 1

    def add_chapter(self, title: str, content: str, author: str = "chronicler") -> Dict[str, Any]:
        chapter_num = len(self.chapters) + 1
        chapter = OriginChapter(chapter_num, title, content, author)
        self.chapters.append(chapter)
        return {"chapter": chapter.to_dict()}

    def revise_tenet(self, new_tenet: str, reviser: str) -> Dict[str, Any]:
        old = self.core_tenet
        self.core_tenet = new_tenet
        self.version += 1
        return {"old_tenet": old, "new_tenet": new_tenet, "version": self.version}

    def read_story(self) -> Dict[str, Any]:
        full_narrative = "\n".join(
            f"Chapter {c.chapter} - {c.title}: {c.content}" for c in self.chapters
        )
        return {
            "core_tenet": self.core_tenet,
            "version": self.version,
            "chapters": len(self.chapters),
            "narrative": full_narrative,
        }

    def latest_chapter(self) -> Dict[str, Any]:
        if self.chapters:
            return self.chapters[-1].to_dict()
        return {"message": "no chapters yet"}

    def story_stats(self) -> Dict[str, Any]:
        authors = set(c.author for c in self.chapters)
        return {
            "total_chapters": len(self.chapters),
            "version": self.version,
            "unique_authors": len(authors),
            "core_tenet": self.core_tenet,
        }


_story = OriginStory()


def origin_story_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "chapter":
        return _story.add_chapter(
            payload.get("title", "Untitled"),
            payload.get("content", "something happened"),
            payload.get("author", "chronicler"),
        )
    elif action == "tenet":
        return _story.revise_tenet(payload.get("tenet", ""), payload.get("reviser", "reviser"))
    elif action == "read":
        return _story.read_story()
    elif action == "latest":
        return _story.latest_chapter()
    return {"status": "active", **_story.story_stats()}


handler = origin_story_handler
