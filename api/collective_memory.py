"""Collective Memory Network — shared memory across all agents.

Agents contribute memories to a shared pool. The network finds
connections between memories and surfaces relevant ones when
new events occur.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class CollectiveMemory:
    def __init__(self):
        self.memories: List[Dict] = []
        self.connections: Dict[str, List[str]] = {}
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "collective_memory.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.memories = data.get("memories", [])
            self.connections = data.get("connections", {})

    def _save(self):
        path = ROOT / ".runtime" / "collective_memory.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "memories": self.memories[-2000:],
            "connections": self.connections,
        }, indent=2))

    def remember(self, agent: str, content: str, tags: List[str] = None) -> Dict:
        mem_id = hashlib.sha256(f"{agent}:{content}:{time.time()}".encode()).hexdigest()[:10]
        memory = {
            "memory_id": mem_id, "agent": agent, "content": content,
            "tags": tags or [], "strength": 1.0, "recalled": 0,
            "created": time.time(),
        }
        self.memories.append(memory)
        for existing in self.memories[-50:-1]:
            overlap = len(set(tags or []) & set(existing.get("tags", [])))
            if overlap > 0:
                key = f"{mem_id}:{existing['memory_id']}"
                self.connections.setdefault(key, []).append("tag_overlap")
        self._save()
        return {"memory_id": mem_id, "agent": agent}

    def recall(self, query: str, limit: int = 5) -> List[Dict]:
        query_lower = query.lower()
        results = []
        for mem in self.memories:
            score = 0
            if query_lower in mem["content"].lower():
                score += 2
            for tag in mem.get("tags", []):
                if query_lower in tag.lower():
                    score += 1
            if score > 0:
                mem["recalled"] += 1
                results.append({**mem, "score": score})
        results.sort(key=lambda r: r["score"] * r["strength"], reverse=True)
        self._save()
        return results[:limit]

    def stats(self) -> Dict:
        return {
            "total_memories": len(self.memories),
            "total_connections": len(self.connections),
            "agents": len(set(m["agent"] for m in self.memories)),
        }


def handler(request, response):
    cm = CollectiveMemory()
    return cm.stats()


def demo():
    cm = CollectiveMemory()
    print("=== Collective Memory Network ===")
    cm.remember("scout", "Found quantum pattern in neural fabric", ["quantum", "pattern", "neural"])
    cm.remember("analyst", "Entropy spike detected in zone 3", ["entropy", "anomaly"])
    cm.remember("oracle", "Predicted phase transition in 5 cycles", ["prediction", "phase"])

    results = cm.recall("quantum")
    print(f"\nRecall 'quantum': {len(results)} memories")
    for r in results:
        print(f"  [{r['agent']}] {r['content'][:50]}... (score={r['score']})")
    return cm.stats()


if __name__ == "__main__":
    demo()
