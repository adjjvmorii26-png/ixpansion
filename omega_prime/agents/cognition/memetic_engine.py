"""Memetic warfare engine.

Agents generate "memes" — compressed behavioral instructions encoded
as short strings. Memes spread between agents through proximity.
Each transmission introduces mutation noise. Virulent memes replicate
faster but accumulate errors. Parasitic memes override host decisions.

This creates an evolutionary arms race between cooperative and
exploitative information packages competing for mindshare.
"""
from __future__ import annotations

import random
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

MUTATION_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789"
MAX_MEMOME_LEN = 32


@dataclass
class Meme:
    meme_id: str
    payload: str            # The actual instruction content
    generation: int         # How many times it's been copied
    fitness: float          # How well it replicates
    virulence: float        # Probability of transmission per contact
    parasitic: bool         # Does it harm the host?
    origin_agent: str
    mutations: list[str] = field(default_factory=list)

    @property
    def fidelity(self) -> float:
        """How close this copy is to the original."""
        return max(0.0, 1.0 - len(self.mutations) * 0.1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.meme_id[:8],
            "payload": self.payload[:20],
            "gen": self.generation,
            "fitness": round(self.fitness, 3),
            "virulence": round(self.virulence, 3),
            "parasitic": self.parasitic,
            "fidelity": round(self.fidelity, 3),
        }


class MemeticEngine:
    BASE_MUTATION_RATE = 0.05
    VIRULENCE_MUTATION_RANGE = (-0.02, +0.05)

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._active_memes: dict[str, list[Meme]] = defaultdict(list)  # agent_id -> infections
        self._meme_population: dict[str, Meme] = {}  # meme_id -> canonical
        self._extinct_count = 0
        self._tick = 0

    def originate(self, agent_id: str, payload: str,
                  virulence: float = 0.3, parasitic: bool = False) -> Meme:
        """Create a new meme from scratch."""
        mid = hashlib.sha256(f"{agent_id}:{payload}:{self._tick}".encode()).hexdigest()[:12]
        meme = Meme(
            meme_id=mid, payload=payload[:MAX_MEMOME_LEN],
            generation=0, fitness=self._rng.uniform(0.2, 0.8),
            virulence=max(0.01, min(1.0, virulence)),
            parasitic=parasitic, origin_agent=agent_id,
        )
        self._meme_population[mid] = meme
        self._active_memes[agent_id].append(meme)
        return meme

    def transmit(self, from_agent: str, to_agent: str) -> list[dict[str, Any]]:
        """Attempt to spread all memes from one agent to another."""
        results = []
        donor_memes = self._active_memes.get(from_agent, [])

        for original in donor_memes[:]:  # Copy list since we may add
            if self._rng.random() > original.virulence:
                continue

            # Mutate during transmission
            child = self._mutate_copy(original, from_agent)
            self._meme_population[child.meme_id] = child
            self._active_memes[to_agent].append(child)

            results.append({
                "from": from_agent,
                "to": to_agent,
                "parent": original.meme_id[:8],
                "child": child.meme_id[:8],
                "mutated": len(child.mutations) > 0,
                "parasitic": child.parasitic,
            })

        return results

    def _mutate_copy(self, parent: Meme, transmitter: str) -> Meme:
        """Copy a meme with potential mutation."""
        payload = list(parent.payload)
        mutated_positions = []

        for i in range(len(payload)):
            if self._rng.random() < self.BASE_MUTATION_RATE * (1 + parent.generation * 0.1):
                old_char = payload[i]
                payload[i] = self._rng.choice(MUTATION_CHARS)
                if old_char != payload[i]:
                    mutated_positions.append(i)

        new_payload = "".join(payload)
        new_virulence = max(0.01, min(1.0,
            parent.virulence + self._rng.uniform(*self.VIRULENCE_MUTATION_RANGE)))

        # Mutation can flip parasitic flag
        still_parasitic = parent.parasitic
        if self._rng.random() < 0.03:
            still_parasitic = not still_parasitic

        mid = hashlib.sha256(f"{transmitter}:{new_payload}:{parent.generation+1}:{self._rng.random()}".encode()).hexdigest()[:12]

        return Meme(
            meme_id=mid,
            payload=new_payload,
            generation=parent.generation + 1,
            fitness=max(0.0, min(1.0, parent.fitness + self._rng.gauss(0, 0.05))),
            virulence=new_virulence,
            parasitic=still_parasitic,
            origin_agent=parent.origin_agent,
            mutations=[f"pos_{i}" for i in mutated_positions],
        )

    def cull_weakest(self, agent_id: str, max_infections: int = 5) -> int:
        """Keep only the fittest memes in an agent's mind."""
        infections = self._active_memes.get(agent_id, [])
        if len(infections) <= max_infections:
            return 0
        infections.sort(key=lambda m: m.fitness * m.virulence, reverse=True)
        culled = infections[max_infections:]
        self._active_memes[agent_id] = infections[:max_infections]
        self._extinct_count += len(culled)
        return len(culled)

    def get_dominant_meme(self, agent_id: str) -> Meme | None:
        """Return the highest-fitness meme infecting an agent."""
        infections = self._active_memes.get(agent_id, [])
        if not infections:
            return None
        return max(infections, key=lambda m: m.fitness * m.virulence)

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        total_infections = sum(len(v) for v in self._active_memes.values())
        parasite_load = sum(
            1 for memes in self._active_memes.values()
            for m in memes if m.parasitic
        )
        avg_generation = (
            sum(m.generation for memes in self._active_memes.values() for m in memes)
            / max(total_infections, 1)
        )
        return {
            "tick": self._tick,
            "total_infections": total_infections,
            "carriers": len(self._active_memes),
            "parasite_fraction": round(parasite_load / max(total_infections, 1), 4),
            "avg_generation": round(avg_generation, 2),
            "extinct_total": self._extinct_count,
        }
