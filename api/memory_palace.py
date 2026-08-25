"""Memory Palace — persistent structured memory architecture for agents.

Agents build a "palace" of interconnected memory rooms. Each room
stores a type of memory (experiences, learnings, predictions, dreams).
Rooms connect through corridors, creating associative recall.

Usage:
    POST /api/palace/create         — create a memory palace
    POST /api/palace/room           — add a room to the palace
    POST /api/palace/store          — store a memory in a room
    POST /api/palace/recall         — associative recall across rooms
    GET  /api/palace/<id>/map       — view palace topology
    GET  /api/palace/<id>/stats     — palace statistics
"""
from __future__ import annotations

import hashlib
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ROOM_TYPES = {
    "experience": {"capacity": 1000, "decay_rate": 0.01, "description": "Raw events and interactions"},
    "learning": {"capacity": 500, "decay_rate": 0.005, "description": "Derived insights and patterns"},
    "prediction": {"capacity": 200, "decay_rate": 0.02, "description": "Future state estimates"},
    "dream": {"capacity": 100, "decay_rate": 0.03, "description": "Creative synthesis outputs"},
    "anomaly": {"capacity": 300, "decay_rate": 0.001, "description": "Unusual occurrences to remember"},
    "relationship": {"capacity": 200, "decay_rate": 0.002, "description": "Agent and system relationships"},
}


class MemoryPalace:
    def __init__(self):
        self.palaces: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "memory_palace.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.palaces = data.get("palaces", {})

    def _save(self):
        path = ROOT / ".runtime" / "memory_palace.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "palaces": self.palaces,
        }, indent=2))

    def create(self, owner: str, name: str = "") -> Dict:
        palace_id = hashlib.sha256(f"{owner}:{name}:{time.time()}".encode()).hexdigest()[:12]
        palace_name = name or f"Palace of {owner}"
        self.palaces[palace_id] = {
            "name": palace_name,
            "owner": owner,
            "rooms": {},
            "corridors": [],
            "created": time.time(),
            "total_memories": 0,
        }
        self._save()
        return {"palace_id": palace_id, "name": palace_name}

    def add_room(self, palace_id: str, room_type: str,
                 room_name: str = "") -> Dict:
        if palace_id not in self.palaces:
            return {"error": "palace not found"}
        if room_type not in ROOM_TYPES:
            return {"error": f"unknown room type: {room_type}. Valid: {list(ROOM_TYPES.keys())}"}
        palace = self.palaces[palace_id]
        room_id = hashlib.sha256(f"{palace_id}:{room_type}:{time.time()}".encode()).hexdigest()[:8]
        rt = ROOM_TYPES[room_type]
        palace["rooms"][room_id] = {
            "type": room_type,
            "name": room_name or f"{room_type}_room",
            "capacity": rt["capacity"],
            "decay_rate": rt["decay_rate"],
            "memories": [],
            "corridor_to": [],
            "created": time.time(),
        }
        self._save()
        return {"room_id": room_id, "type": room_type, "capacity": rt["capacity"]}

    def store(self, palace_id: str, room_id: str,
              content: str, tags: List[str] = None,
              strength: float = 1.0) -> Dict:
        if palace_id not in self.palaces:
            return {"error": "palace not found"}
        palace = self.palaces[palace_id]
        if room_id not in palace["rooms"]:
            return {"error": "room not found"}
        room = palace["rooms"][room_id]
        if len(room["memories"]) >= room["capacity"]:
            return {"error": "room is full"}
        memory_id = hashlib.sha256(f"{content}:{time.time()}".encode()).hexdigest()[:10]
        memory = {
            "memory_id": memory_id,
            "content": content,
            "tags": tags or [],
            "strength": min(strength, 1.0),
            "access_count": 0,
            "stored_at": time.time(),
        }
        room["memories"].append(memory)
        palace["total_memories"] += 1
        self._save()
        return {"memory_id": memory_id, "room": room["name"]}

    def recall(self, palace_id: str, query: str, limit: int = 5) -> List[Dict]:
        if palace_id not in self.palaces:
            return []
        palace = self.palaces[palace_id]
        results = []
        query_lower = query.lower()
        for room_id, room in palace["rooms"].items():
            for memory in room["memories"]:
                score = 0
                if query_lower in memory["content"].lower():
                    score += 2
                for tag in memory["tags"]:
                    if query_lower in tag.lower():
                        score += 1
                if score > 0:
                    memory["access_count"] += 1
                    memory["strength"] = min(1.0, memory["strength"] + 0.05)
                    results.append({
                        "memory_id": memory["memory_id"],
                        "content": memory["content"],
                        "room": room["name"],
                        "room_type": room["type"],
                        "score": score,
                        "strength": memory["strength"],
                        "tags": memory["tags"],
                    })
        results.sort(key=lambda r: r["score"] * r["strength"], reverse=True)
        self._save()
        return results[:limit]

    def palace_map(self, palace_id: str) -> Dict:
        if palace_id not in self.palaces:
            return {"error": "palace not found"}
        palace = self.palaces[palace_id]
        rooms = []
        for rid, room in palace["rooms"].items():
            rooms.append({
                "id": rid,
                "type": room["type"],
                "name": room["name"],
                "memory_count": len(room["memories"]),
                "capacity": room["capacity"],
            })
        corridors = palace.get("corridors", [])
        return {
            "palace_id": palace_id,
            "name": palace["name"],
            "rooms": rooms,
            "corridors": corridors,
            "total_memories": palace["total_memories"],
        }

    def palace_stats(self, palace_id: str) -> Dict:
        if palace_id not in self.palaces:
            return {"error": "palace not found"}
        palace = self.palaces[palace_id]
        room_stats = {}
        for rid, room in palace["rooms"].items():
            room_stats[room["type"]] = {
                "count": len(room["memories"]),
                "capacity": room["capacity"],
                "utilization": round(len(room["memories"]) / max(room["capacity"], 1), 4),
            }
        return {
            "palace_id": palace_id,
            "name": palace["name"],
            "total_rooms": len(palace["rooms"]),
            "total_memories": palace["total_memories"],
            "rooms": room_stats,
        }


def handler(request, response):
    mp = MemoryPalace()
    return {"room_types": list(ROOM_TYPES.keys()), "total_palaces": len(mp.palaces)}


def demo():
    mp = MemoryPalace()
    print("=== Memory Palace ===")
    palace = mp.create("architect_1", "The Infinite Archive")
    print(f"\nPalace created: {palace['name']} ({palace['palace_id']})")

    exp_room = mp.add_room(palace["palace_id"], "experience", "Event Hall")
    learn_room = mp.add_room(palace["palace_id"], "learning", "Library")
    dream_room = mp.add_room(palace["palace_id"], "dream", "Dreaming Chamber")
    print(f"Rooms added: {exp_room['room_id']}, {learn_room['room_id']}, {dream_room['room_id']}")

    mp.store(palace["palace_id"], exp_room["room_id"],
             "The quantum experiment produced unexpected phase transition",
             tags=["quantum", "phase_transition"], strength=0.9)
    mp.store(palace["palace_id"], learn_room["room_id"],
             "Phase transitions correlate with entropy spikes above 0.7",
             tags=["quantum", "entropy", "correlation"], strength=0.8)
    mp.store(palace["palace_id"], dream_room["room_id"],
             "A dream of fractals growing inside a quantum lattice",
             tags=["dream", "fractal", "quantum"], strength=0.6)

    results = mp.recall(palace["palace_id"], "quantum")
    print(f"\nRecall 'quantum': {len(results)} memories found")
    for r in results:
        print(f"  [{r['room_type']}] {r['content'][:60]}... (score={r['score']})")

    stats = mp.palace_stats(palace["palace_id"])
    print(f"\nPalace: {stats['total_rooms']} rooms, {stats['total_memories']} memories")

    return stats


if __name__ == "__main__":
    demo()
