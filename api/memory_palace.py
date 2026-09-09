"""Wave 516: Memory Palace — spatial organization of organism memories."""
from __future__ import annotations
import json, os, time
from typing import Any, Dict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    rooms = []
    if os.path.isdir(DATA_DIR):
        for fname in sorted(os.listdir(DATA_DIR)):
            if fname.endswith(".json"):
                path = os.path.join(DATA_DIR, fname)
                mtime = os.path.getmtime(path)
                age_days = round((time.time() - mtime) / 86400, 1)
                try:
                    sz = os.path.getsize(path)
                except Exception:
                    sz = 0
                rooms.append({
                    "name": fname.replace(".json", ""),
                    "age_days": age_days,
                    "size_bytes": sz,
                    "era": "primordial" if age_days > 30 else "recent" if age_days < 1 else "contemporary",
                })
    rooms.sort(key=lambda r: r["age_days"], reverse=True)
    return {
        "action": "memory_palace",
        "rooms": rooms[:50],
        "total_rooms": len(rooms),
        "eras": {
            "primordial": sum(1 for r in rooms if r["era"] == "primordial"),
            "contemporary": sum(1 for r in rooms if r["era"] == "contemporary"),
            "recent": sum(1 for r in rooms if r["era"] == "recent"),
        },
        "time": time.time(),
        "vitals": coherence_vitals(),
    }


class MemoryPalace:
    """Spatial memory organization — memories stored in named rooms within palaces."""

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or DATA_DIR
        os.makedirs(self.data_dir, exist_ok=True)
        self._palaces = {}
        self._palace_db = os.path.join(self.data_dir, "memory_palaces.json")
        self._load()

    def _load(self):
        try:
            with open(self._palace_db, "r") as f:
                self._palaces = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._palaces = {}

    def _save(self):
        with open(self._palace_db, "w") as f:
            json.dump(self._palaces, f, indent=2)

    def create(self, user: str, name: str = "Memory Palace") -> Dict[str, Any]:
        palace_id = f"palace_{user}_{int(time.time())}"
        self._palaces[palace_id] = {"user": user, "name": name, "rooms": {}, "created": time.time()}
        self._save()
        return {"palace_id": palace_id, "user": user, "name": name}

    def add_room(self, palace_id: str, room_type: str, name: str = "") -> Dict[str, Any]:
        if palace_id not in self._palaces:
            return {"error": "palace not found"}
        room_id = f"room_{int(time.time())}_{len(self._palaces[palace_id]['rooms'])}"
        self._palaces[palace_id]["rooms"][room_id] = {
            "type": room_type, "name": name or room_type.capitalize(), "memories": []
        }
        self._save()
        return {"room_id": room_id, "type": room_type, "name": name or room_type.capitalize()}

    def store(self, palace_id: str, room_id: str, content: str, tags=None) -> Dict[str, Any]:
        if palace_id not in self._palaces or room_id not in self._palaces[palace_id]["rooms"]:
            return {"error": "palace or room not found"}
        memory = {
            "memory_id": f"mem_{int(time.time() * 1000)}",
            "content": content, "tags": tags or [], "stored_at": time.time()
        }
        self._palaces[palace_id]["rooms"][room_id]["memories"].append(memory)
        self._save()
        return memory

    def recall(self, palace_id: str, query: str, limit: int = 10) -> list:
        results = []
        q = query.lower()
        for room in self._palaces.get(palace_id, {}).get("rooms", {}).values():
            for m in room["memories"]:
                if q in m["content"].lower() or any(q in t.lower() for t in m["tags"]):
                    results.append(m)
        return results[:limit]

    def palace_map(self, palace_id: str) -> Dict[str, Any]:
        rooms = self._palaces.get(palace_id, {}).get("rooms", {})
        return {"palace_id": palace_id, "rooms": [
            {"room_id": rid, "type": r["type"], "name": r["name"], "memories": len(r["memories"])}
            for rid, r in rooms.items()
        ]}

    def palace_stats(self, palace_id: str) -> Dict[str, Any]:
        rooms = self._palaces.get(palace_id, {}).get("rooms", {})
        total_memories = sum(len(r["memories"]) for r in rooms.values())
        return {"total_rooms": len(rooms), "total_memories": total_memories,
                "palace_id": palace_id}
