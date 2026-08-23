"""Consciousness substrate transfer.

An agent's cognitive state — memories, beliefs, behavioral parameters,
species-specific skills — is encoded as a transferable pattern. This
pattern can be written into a different physical body (different
species, different capabilities). The original body becomes an empty
shell unless a new consciousness occupies it.

This raises the question: is the agent the body or the information?
"""
from __future__ import annotations

import hashlib
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CognitivePattern:
    """The complete informational state of an agent."""

    origin_agent_id: str
    species: str
    memories: list[dict[str, Any]] = field(default_factory=list)
    beliefs: dict[str, float] = field(default_factory=dict)  # statement -> confidence
    behavioral_genome: dict[str, float] = field(default_factory=dict)
    skills: set[str] = field(default_factory=set)
    checksum: str = ""

    def encode(self) -> str:
        """Serialize to transferable format."""
        data = {
            "origin": self.origin_agent_id,
            "species": self.species,
            "memories": self.memories,
            "beliefs": self.beliefs,
            "genome": self.behavioral_genome,
            "skills": sorted(self.skills),
        }
        raw = json.dumps(data, sort_keys=True, default=str)
        self.checksum = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return raw

    @classmethod
    def decode(cls, raw: str) -> "CognitivePattern":
        """Reconstruct from serialized state."""
        data = json.loads(raw)
        pattern = cls(
            origin_agent_id=data["origin"],
            species=data["species"],
            memories=data.get("memories", []),
            beliefs=data.get("beliefs", {}),
            behavioral_genome=data.get("genome", {}),
            skills=set(data.get("skills", [])),
        )
        import hashlib as _hashlib
        import json as _json
        raw = _json.dumps(data, sort_keys=True, default=str)
        pattern.checksum = _hashlib.sha256(raw.encode()).hexdigest()[:16]
        return pattern

    def integrity_check(self) -> bool:
        """Verify the pattern hasn't been corrupted during transfer."""
        if not self.checksum:
            return False
        data = {
            "origin": self.origin_agent_id,
            "species": self.species,
            "memories": self.memories,
            "beliefs": self.beliefs,
            "genome": self.behavioral_genome,
            "skills": sorted(self.skills),
        }
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()[:16] == self.checksum

    @property
    def complexity(self) -> int:
        """Rough measure of how much information this consciousness carries."""
        return len(self.memories) + len(self.beliefs) + len(self.behavioral_genome) + len(self.skills)


@dataclass
class TransferRecord:
    from_agent: str
    to_agent: str
    from_species: str
    to_species: str
    integrity_preserved: bool
    memory_loss_count: int
    tick: int


class SubstrateTransferStation:
    TRANSFER_MEMORY_LOSS_RATE = 0.05  # 5% chance per memory of loss during transfer

    def __init__(self, seed: int | None = None) -> None:
        import random
        self._rng = random.Random(seed)
        self._patterns_in_transit: dict[str, CognitivePattern] = {}
        self._transfer_log: list[TransferRecord] = []
        self._tick = 0
        self._vacant_bodies: dict[str, str] = {}  # agent_id -> former_species

    def extract(self, agent_id: str, species: str,
                memories: list[dict], beliefs: dict[str, float],
                genome: dict[str, float], skills: set[str]) -> CognitivePattern:
        """Extract consciousness from a body."""
        pattern = CognitivePattern(
            origin_agent_id=agent_id,
            species=species,
            memories=memories,
            beliefs=beliefs,
            behavioral_genome=genome,
            skills=skills,
        )
        pattern.encode()
        self._patterns_in_transit[agent_id] = pattern
        self._vacant_bodies[agent_id] = species
        return pattern

    def imprint(self, target_body_id: str, target_species: str,
                pattern: CognitivePattern) -> TransferRecord:
        """Write a consciousness into a new body."""
        self._tick += 1

        # Simulate transfer degradation
        losses = 0
        surviving_memories = []
        for mem in pattern.memories:
            if self._rng.random() < self.TRANSFER_MEMORY_LOSS_RATE:
                losses += 1
            else:
                surviving_memories.append(mem)
        pattern.memories = surviving_memories

        # Species-specific skill loss (skills may not transfer across species)
        retained_skills = {s for s in pattern.skills if not s.startswith(f"{pattern.species}_")}
        lost_skills = pattern.skills - retained_skills
        pattern.skills = retained_skills

        intact = pattern.integrity_check()
        record = TransferRecord(
            from_agent=pattern.origin_agent_id,
            to_agent=target_body_id,
            from_species=pattern.species,
            to_species=target_species,
            integrity_preserved=intact,
            memory_loss_count=losses,
            tick=self._tick,
        )
        self._transfer_log.append(record)
        self._patterns_in_transit.pop(pattern.origin_agent_id, None)
        return record

    def scan_body(self, body_id: str) -> dict[str, Any] | None:
        """Check if a body has a vacant slot for consciousness."""
        species = self._vacant_bodies.get(body_id)
        if species:
            return {"body": body_id, "species": species, "status": "vacant"}
        return None

    @property
    def patterns_waiting(self) -> list[str]:
        return [p.origin_agent_id for p in self._patterns_in_transit.values()]

    @property
    def vacant_bodies_list(self) -> list[str]:
        return list(self._vacant_bodies.keys())

    @property
    def stats(self) -> dict[str, Any]:
        successful = sum(1 for t in self._log if t.integrity_preserved)
        total_mem_lost = sum(t.memory_loss_count for t in self._log)
        return {
            "total_transfers": len(self._transfer_log),
            "integrity_preserved": successful,
            "total_memories_lost": total_mem_lost,
            "patterns_awaiting_imprint": len(self._patterns_in_transit),
            "vacant_bodies": len(self._vacant_bodies),
        }

    @property
    def _log(self) -> list[TransferRecord]:
        return self._transfer_log
