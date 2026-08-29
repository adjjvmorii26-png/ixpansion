"""Wave 131 — Collaboration Hub.

A shared space where workers coordinate on group tasks. Tasks are
broken into chunks distributed to team members, and communication
between workers is journaled as a shared narrative that informs
later task routing.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class CollaborationMessage:
    """A message exchanged between workers in the hub."""

    def __init__(self, author: str, text: str, topic: str = "general"):
        self.author = author
        self.text = text
        self.topic = topic
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"msg:{author}:{text}".encode()).hexdigest()[:10]

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "author": self.author, "topic": self.topic,
                "text": self.text, "timestamp": round(self.timestamp, 4)}


class GroupTask:
    """A task executed collaboratively by multiple workers."""

    def __init__(self, title: str, members: List[str], chunks: int = 2):
        self.title = title
        self.members = members
        self.chunk_count = chunks
        self.chunks_done = 0
        self.status = "assembling"
        self.notes: List[str] = []
        self.created = time.time()

    def assign_chunk(self) -> bool:
        if self.chunks_done >= self.chunk_count:
            return False
        self.chunks_done += 1
        if self.chunks_done >= self.chunk_count:
            self.status = "merging"
        return True

    def merge(self) -> str:
        if self.chunks_done < self.chunk_count:
            self.status = "blocked"
            return "blocked"
        self.status = "completed"
        return self.status

    def note(self, author: str, text: str) -> None:
        self.notes.append(f"[{author}] {text}")

    def to_dict(self) -> Dict[str, Any]:
        return {"title": self.title, "members": self.members,
                "chunks_done": self.chunks_done, "chunk_count": self.chunk_count,
                "status": self.status, "notes": len(self.notes)}


class CollaborationHub:
    """Shared coordination space for worker groups."""

    def __init__(self):
        self._tasks: Dict[str, GroupTask] = {}
        self._messages: List[CollaborationMessage] = []
        self._conversations = 0

    def create_group_task(self, title: str, members: List[str], chunks: int = 2) -> GroupTask:
        task = GroupTask(title, members, chunks)
        key = hashlib.sha256(f"gtask:{title}".encode()).hexdigest()[:10]
        task.id = key
        self._tasks[key] = task
        return task

    def progress_group_task(self, key: str) -> bool:
        task = self._tasks.get(key)
        if task is None:
            return False
        return task.assign_chunk()

    def complete_group_task(self, key: str) -> str:
        task = self._tasks.get(key)
        if task is None:
            return "missing"
        return task.merge()

    def post_message(self, author: str, text: str, topic: str = "general") -> CollaborationMessage:
        msg = CollaborationMessage(author, text, topic)
        self._messages.append(msg)
        self._conversations += 1
        return msg

    def messages(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        selected = (m for m in self._messages if topic is None or m.topic == topic)
        return [m.to_dict() for m in selected]

    def status(self) -> Dict[str, Any]:
        return {"group_tasks": len(self._tasks), "messages": len(self._messages),
                "conversations": self._conversations,
                "completed_tasks": sum(1 for t in self._tasks.values() if t.status == "completed")}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    hub = CollaborationHub()
    return {"status": "active", "module": "collaboration_hub",
            **hub.status()}
