from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class MemoryRoom:
    def __init__(self, name, dimension):
        self.name = name; self.dimension = dimension; self.artifacts = []
    def store(self, artifact): self.artifacts.append(artifact)
    def recall(self, index): return self.artifacts[index] if index < len(self.artifacts) else None

class MemoryPalace:
    def __init__(self, seed=42):
        self.seed = seed; self.rooms = {}
    def build_room(self, name, dimension="abstract"):
        self.rooms[name] = MemoryRoom(name, dimension)
    def store_memory(self, room_name, memory):
        if room_name in self.rooms: self.rooms[room_name].store(memory)
    def recall_memory(self, room_name, index):
        if room_name in self.rooms: return self.rooms[room_name].recall(index)
        return None
    def total_memories(self):
        return sum(len(r.artifacts) for r in self.rooms.values())
    def report(self):
        return {"palace": "memory_palace_architect",
                "rooms": {n: {"dimension": r.dimension, "artifacts": len(r.artifacts)} for n, r in self.rooms.items()},
                "total_memories": self.total_memories()}

def demo():
    p = MemoryPalace(42)
    p.build_room("void", "spatial"); p.build_room("lattice", "temporal")
    p.build_room("continuum", "causal"); p.build_room("fractal", "recursive")
    for room in ["void", "lattice", "continuum", "fractal"]:
        for i in range(5): p.store_memory(room, {"id": f"{room}_{i}", "strength": 0.5 + i*0.1})
    return p.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
