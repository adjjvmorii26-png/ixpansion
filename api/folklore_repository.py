"""Wave 126 — Folklore Repository.

Stores and organises the system's accumulated folklore — tales of
past triumphs, cautionary warnings, best practices encoded as
folk wisdom, and collective knowledge passed between generations.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class FolkTale:
    """A piece of folk wisdom or lore."""

    def __init__(self, title: str, lesson: str, category: str = "wisdom"):
        self.title = title
        self.lesson = lesson
        self.category = category
        self.told_count = 0
        self.created = time.time()
        self.id = hashlib.sha256(f"folk:{title}".encode()).hexdigest()[:10]

    def tell(self) -> Dict[str, Any]:
        self.told_count += 1
        return {"title": self.title, "lesson": self.lesson, "told_count": self.told_count}

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "title": self.title, "lesson": self.lesson,
                "category": self.category, "told_count": self.told_count}


class FolkloreRepository:
    """Stores and manages folk wisdom."""

    def __init__(self):
        self._tales: List[FolkTale] = []
        self._total_told = 0

    def add_tale(self, title: str, lesson: str, category: str = "wisdom") -> FolkTale:
        tale = FolkTale(title, lesson, category)
        self._tales.append(tale)
        return tale

    def tell_tale(self, tale_id: str) -> Dict[str, Any]:
        for tale in self._tales:
            if tale.id == tale_id:
                self._total_told += 1
                return tale.tell()
        return {"error": "tale not found"}

    def by_category(self, category: str) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self._tales if t.category == category]

    def most_told(self) -> Dict[str, Any]:
        if not self._tales:
            return {}
        return max(self._tales, key=lambda t: t.told_count).to_dict()

    def status(self) -> Dict[str, Any]:
        categories = {}
        for t in self._tales:
            categories[t.category] = categories.get(t.category, 0) + 1
        return {"total_tales": len(self._tales), "total_told": self._total_told,
                "categories": categories}
