"""Memory Weave — threads memories from multiple agents into shared tapestries.

Individual memories are private, but when agents agree to share, their
memories weave together into tapestries — collaborative memory structures
that no single agent could create alone. The weave reveals connections
between experiences that individuals miss.
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


class MemoryThread:
    def __init__(self, agent_id: str, content: str, emotional_valence: float = 0.0):
        self.agent_id = agent_id
        self.content = content
        self.emotional_valence = emotional_valence
        self.timestamp = time.time()
        self.thread_id = hashlib.sha256(f"{agent_id}:{content}".encode()).hexdigest()[:8]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "agent_id": self.agent_id,
            "content": self.content[:80],
            "emotional_valence": round(self.emotional_valence, 3),
        }


class Tapestry:
    def __init__(self, name: str):
        self.name = name
        self.threads: List[MemoryThread] = []
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{name}:{self.created_at}".encode()).hexdigest()[:8]

    def add_thread(self, thread: MemoryThread):
        self.threads.append(thread)

    def weave_pattern(self) -> Dict[str, Any]:
        if not self.threads:
            return {"pattern": "empty"}
        agents = list(set(t.agent_id for t in self.threads))
        avg_valence = sum(t.emotional_valence for t in self.threads) / len(self.threads)
        emotional_range = max(t.emotional_valence for t in self.threads) - min(t.emotional_valence for t in self.threads)
        return {
            "name": self.name,
            "threads": len(self.threads),
            "unique_agents": len(agents),
            "agents": agents,
            "avg_valence": round(avg_valence, 3),
            "emotional_range": round(emotional_range, 3),
            "richness": round(min(len(self.threads) / 5, 1.0), 3),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "threads": len(self.threads),
            "pattern": self.weave_pattern(),
        }


class MemoryWeave:
    def __init__(self):
        self.tapestries: Dict[str, Tapestry] = {}
        self.shared_memories: List[MemoryThread] = []

    def share_memory(self, agent_id: str, content: str, valence: float = 0.0) -> Dict[str, Any]:
        thread = MemoryThread(agent_id, content, valence)
        self.shared_memories.append(thread)
        return {"shared": thread.to_dict()}

    def create_tapestry(self, name: str) -> Dict[str, Any]:
        tapestry = Tapestry(name)
        self.tapestries[tapestry.id] = tapestry
        return {"created": tapestry.to_dict()}

    def weave_into(self, tapestry_id: str, thread_ids: List[str]) -> Dict[str, Any]:
        if tapestry_id not in self.tapestries:
            return {"error": "tapestry not found"}
        tapestry = self.tapestries[tapestry_id]
        woven = 0
        for thread in self.shared_memories:
            if thread.thread_id in thread_ids:
                tapestry.add_thread(thread)
                woven += 1
        return {"woven": woven, "tapestry": tapestry.to_dict()}

    def discover_connections(self, tapestry_id: str) -> List[Dict[str, Any]]:
        if tapestry_id not in self.tapestries:
            return []
        tapestry = self.tapestries[tapestry_id]
        connections = []
        threads = tapestry.threads
        for i in range(len(threads)):
            for j in range(i + 1, len(threads)):
                if threads[i].agent_id != threads[j].agent_id:
                    valence_sim = 1.0 - abs(threads[i].emotional_valence - threads[j].emotional_valence)
                    if valence_sim > 0.7:
                        connections.append({
                            "agents": [threads[i].agent_id, threads[j].agent_id],
                            "connection_strength": round(valence_sim, 3),
                            "content_a": threads[i].content[:30],
                            "content_b": threads[j].content[:30],
                        })
        return connections

    def weave_stats(self) -> Dict[str, Any]:
        return {
            "total_tapestries": len(self.tapestries),
            "shared_memories": len(self.shared_memories),
            "total_threads_woven": sum(len(t.threads) for t in self.tapestries.values()),
        }


_weave = MemoryWeave()


def memory_weave_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "share":
        return _weave.share_memory(
            payload.get("agent_id", "memory_holder"),
            payload.get("content", "a memory"),
            payload.get("valence", 0.0),
        )
    elif action == "create_tapestry":
        return _weave.create_tapestry(payload.get("name", "untitled_tapestry"))
    elif action == "weave":
        return _weave.weave_into(
            payload.get("tapestry_id", ""),
            payload.get("thread_ids", []),
        )
    elif action == "connections":
        return {"connections": _weave.discover_connections(payload.get("tapestry_id", ""))}
    return {"status": "active", **_weave.weave_stats()}


handler = memory_weave_handler
