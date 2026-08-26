"""Wave 124 — Memesis Chronicle.

Chronicles the evolution of memes — self-replicating ideas that spread
through the system, mutating as they propagate. Tracks memetic lineages,
fitness landscapes, and extinction events.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class Meme:
    """A self-replicating idea unit."""

    def __init__(self, content: str, fitness: float = 0.5):
        self.content = content
        self.fitness = fitness
        self.created = time.time()
        self.replications = 0
        self.mutations = 0
        self.id = hashlib.sha256(f"meme:{content}".encode()).hexdigest()[:10]
        self.ancestors: List[str] = []
        self.descendants: List[str] = []

    def replicate(self) -> "Meme":
        self.replications += 1
        child = Meme(self.content, fitness=self.fitness * 0.95)
        child.ancestors.append(self.id)
        self.descendants.append(child.id)
        return child

    def mutate(self, new_content: str) -> "Meme":
        self.mutations += 1
        mutant = Meme(new_content, fitness=min(1.0, self.fitness + 0.05))
        mutant.ancestors.append(self.id)
        self.descendants.append(mutant.id)
        return mutant

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "content": self.content[:50],
                "fitness": round(self.fitness, 4), "replications": self.replications,
                "mutations": self.mutations, "age": round(time.time() - self.created, 2)}


class MemesisChronicle:
    """Tracks memetic evolution across the system."""

    def __init__(self):
        self._memes: Dict[str, Meme] = {}
        self._extinction_events: List[str] = []
        self._generation = 0

    def introduce(self, content: str, fitness: float = 0.5) -> Meme:
        meme = Meme(content, fitness)
        self._memes[meme.id] = meme
        return meme

    def evolve(self, meme_id: str) -> Optional[Meme]:
        meme = self._memes.get(meme_id)
        if not meme:
            return None
        child = meme.replicate()
        self._memes[child.id] = child
        self._generation += 1
        return child

    def mutate_meme(self, meme_id: str, new_content: str) -> Optional[Meme]:
        meme = self._memes.get(meme_id)
        if not meme:
            return None
        mutant = meme.mutate(new_content)
        self._memes[mutant.id] = mutant
        self._generation += 1
        return mutant

    def fitness_landscape(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in sorted(self._memes.values(), key=lambda x: x.fitness, reverse=True)]

    def extinct_memes(self, threshold: float = 0.1) -> List[Dict[str, Any]]:
        extinct = [m.to_dict() for m in self._memes.values() if m.fitness < threshold]
        for m in extinct:
            self._extinction_events.append(m["id"])
        return extinct

    def status(self) -> Dict[str, Any]:
        return {"total_memes": len(self._memes), "generation": self._generation,
                "extinction_events": len(self._extinction_events)}
