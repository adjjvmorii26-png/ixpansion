"""Search engine for engine memories — indexes all archived events."""
from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryEcho:
    echo_id: str
    content: str
    source: str  # chronicle, anomaly, dream
    tick: int
    tags: set[str] = field(default_factory=set)

    def relevance(self, query_tags: set[str]) -> float:
        if not query_tags or not self.tags:
            return 0.0
        overlap = query_tags & self.tags
        union = query_tags | self.tags
        return len(overlap) / len(union) if union else 0.0


class EchoIndex:
    def __init__(self) -> None:
        self._memories: dict[str, MemoryEcho] = {}
        self._inverted: dict[str, set[str]] = defaultdict(set)  # tag -> echo_ids

    def remember(self, content: str, source: str, tick: int,
                 tags: set[str] | None = None) -> str:
        eid = hashlib.sha256(f"{source}:{tick}:{content[:50]}".encode()).hexdigest()[:12]
        echo = MemoryEcho(echo_id=eid, content=content, source=source,
                          tick=tick, tags=tags or set())
        self._memories[eid] = echo
        for tag in echo.tags:
            self._inverted[tag].add(eid)
        return eid

    def search(self, query_tags: set[str], min_relevance: float = 0.1,
               limit: int = 10) -> list[dict[str, Any]]:
        candidates = set()
        for tag in query_tags:
            candidates |= self._inverted.get(tag, set())

        scored = []
        for eid in candidates:
            echo = self._memories[eid]
            rel = echo.relevance(query_tags)
            if rel >= min_relevance:
                scored.append((rel, echo))

        scored.sort(key=lambda x: (-x[0], -x[1].tick))
        return [
            {"id": e.echo_id, "content": e.content[:100],
             "relevance": round(rel, 4), "source": e.source, "tick": e.tick}
            for rel, e in scored[:limit]
        ]

    def forget(self, echo_id: str) -> bool:
        if echo_id in self._memories:
            echo = self._memories.pop(echo_id)
            for tag in echo.tags:
                self._inverted[tag].discard(echo_id)
            return True
        return False

    @property
    def stats(self) -> dict[str, Any]:
        by_source = defaultdict(int)
        for m in self._memories.values():
            by_source[m.source] += 1
        return {"total_memories": len(self._memories), "by_source": dict(by_source)}
