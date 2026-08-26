"""Dream Architect — designs and builds structured dream environments.

Unlike random dreams, the Dream Architect constructs intentional dream
spaces: labyrinths of meaning, libraries of forgotten knowledge, gardens
of impossible beauty. Agents can visit these designed dreams for
inspiration, training, or contemplation.
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

ROOM_TYPES = {
    "library": {"mood": "contemplative", "discovery_chance": 0.4},
    "garden": {"mood": "peaceful", "discovery_chance": 0.3},
    "labyrinth": {"mood": "tense", "discovery_chance": 0.6},
    "observatory": {"mood": "curious", "discovery_chance": 0.5},
    "forge": {"mood": "energetic", "discovery_chance": 0.3},
    "void": {"mood": "unsettling", "discovery_chance": 0.8},
    "throne": {"mood": "authoritative", "discovery_chance": 0.2},
}


class DreamRoom:
    def __init__(self, name: str, room_type: str, description: str):
        self.name = name
        self.room_type = room_type
        self.description = description
        self.specs = ROOM_TYPES.get(room_type, ROOM_TYPES["library"])
        self.visitors: List[str] = []
        self.discoveries: List[str] = []
        self.id = hashlib.sha256(f"{name}:{room_type}".encode()).hexdigest()[:8]

    def visit(self, agent_id: str) -> Dict[str, Any]:
        self.visitors.append(agent_id)
        discovered = random.random() < self.specs["discovery_chance"]
        if discovered:
            insight = f"discovered in {self.name}: {random.choice(['a hidden pattern', 'an ancient truth', 'a future memory', 'an impossible equation'])}"
            self.discoveries.append(insight)
        return {
            "room": self.name,
            "type": self.room_type,
            "mood": self.specs["mood"],
            "discovered": discovered,
            "insight": self.discoveries[-1] if discovered else None,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.room_type,
            "description": self.description[:60],
            "visitors": len(self.visitors),
            "discoveries": len(self.discoveries),
        }


class DreamArchitect:
    def __init__(self):
        self.dreamscapes: Dict[str, List[DreamRoom]] = {}
        self.visit_log: List[Dict[str, Any]] = []

    def create_dreamscape(self, name: str) -> Dict[str, Any]:
        self.dreamscapes[name] = []
        return {"dreamscape": name, "rooms": 0}

    def add_room(self, dreamscape: str, name: str, room_type: str, description: str = "") -> Dict[str, Any]:
        if dreamscape not in self.dreamscapes:
            self.create_dreamscape(dreamscape)
        room = DreamRoom(name, room_type, description or f"a {room_type}")
        self.dreamscapes[dreamscape].append(room)
        return {"room": room.to_dict()}

    def visit_room(self, dreamscape: str, room_id: str, agent_id: str) -> Dict[str, Any]:
        if dreamscape not in self.dreamscapes:
            return {"error": "dreamscape not found"}
        for room in self.dreamscapes[dreamscape]:
            if room.id == room_id:
                result = room.visit(agent_id)
                self.visit_log.append({**result, "agent": agent_id, "dreamscape": dreamscape, "time": time.time()})
                return result
        return {"error": "room not found"}

    def dreamscape_overview(self, dreamscape: str) -> Dict[str, Any]:
        if dreamscape not in self.dreamscapes:
            return {"error": "dreamscape not found"}
        rooms = self.dreamscapes[dreamscape]
        type_counts: Dict[str, int] = {}
        for r in rooms:
            type_counts[r.room_type] = type_counts.get(r.room_type, 0) + 1
        return {
            "dreamscape": dreamscape,
            "rooms": len(rooms),
            "type_distribution": type_counts,
            "total_visitors": sum(len(r.visitors) for r in rooms),
        }

    def architect_stats(self) -> Dict[str, Any]:
        total_rooms = sum(len(r) for r in self.dreamscapes.values())
        return {
            "total_dreamscapes": len(self.dreamscapes),
            "total_rooms": total_rooms,
            "total_visits": len(self.visit_log),
            "total_discoveries": sum(
                sum(len(room.discoveries) for room in rooms) for rooms in self.dreamscapes.values()
            ),
        }


_architect = DreamArchitect()


def dream_architect_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "create":
        return _architect.create_dreamscape(payload.get("name", "untitled_dream"))
    elif action == "add_room":
        return _architect.add_room(
            payload.get("dreamscape", ""),
            payload.get("name", "room"),
            payload.get("room_type", "library"),
            payload.get("description", ""),
        )
    elif action == "visit":
        return _architect.visit_room(
            payload.get("dreamscape", ""),
            payload.get("room_id", ""),
            payload.get("agent_id", "dreamer"),
        )
    elif action == "overview":
        return _architect.dreamscape_overview(payload.get("dreamscape", ""))
    return {"status": "active", **_architect.architect_stats()}
