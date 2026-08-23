"""Memetic immune system — cognitive defense against parasitic ideas.

After exposure to a meme pattern, agents develop "antibodies" —
partial immunity that reduces future infection probability. Antibodies
decay over time (memory fades). Parasitic memes trigger stronger
immune responses than beneficial ones.

This creates a co-evolutionary arms race: memes evolve new payloads
to evade detection; hosts develop broader antibody spectrums.
"""
from __future__ import annotations

import hashlib
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Antibody:
    """Cognitive resistance to a specific meme signature."""

    signature: str          # Hash of the meme payload pattern
    strength: float         # 0-1, how resistant the host is
    exposures: int = 1     # Times this meme was encountered
    tick_created: int = 0

    @property
    def is_effective(self) -> bool:
        return self.strength >= 0.1


class MemeticImmuneSystem:
    BASE_IMMUNE_RESPONSE = 0.15
    PARASITE_BOOST = 0.25
    NATURAL_DECAY = 0.01
    CROSS_IMMUNITY_RADIUS = 0.3  # Similar memes also partially blocked

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._antibodies: dict[str, dict[str, Antibody]] = defaultdict(dict)  # agent_id -> sig -> ab
        self._immune_memory: dict[str, int] = defaultdict(int)  # agent_id -> total infections survived
        self._tick = 0

    def _signature(self, payload: str) -> str:
        return hashlib.sha256(payload.encode()).hexdigest()[:12]

    def expose(self, agent_id: str, meme_payload: str,
               is_parasitic: bool = False) -> dict[str, Any]:
        """Host encounters a meme; immune system responds."""
        self._tick += 1
        sig = self._signature(meme_payload)
        antibodies = self._antibodies[agent_id]

        if sig in antibodies:
            # Secondary exposure — boost existing antibody
            ab = antibodies[sig]
            ab.exposures += 1
            boost = self.BASE_IMMUNE_RESPONSE * (1.5 if is_parasitic else 1.0)
            ab.strength = min(1.0, ab.strength + boost)
            response = "secondary"
        else:
            # Primary exposure — create new antibody
            strength = self.BASE_IMMUNE_RESPONSE + (
                self.PARASITE_BOOST if is_parasitic else 0.0
            )
            antibodies[sig] = Antibody(
                signature=sig, strength=min(1.0, strength), tick_created=self._tick,
            )
            response = "primary"

        # Cross-immunity: similar memes also get partial antibodies
        cross_protected = 0
        for other_sig, other_ab in antibodies.items():
            if other_sig != sig and not other_ab.is_effective:
                similarity = 1.0 - abs(
                    int(sig[:8], 16) - int(other_sig[:8], 16)
                ) / 0xFFFFFFFF
                if similarity > (1.0 - self.CROSS_IMMUNITY_RADIUS):
                    other_ab.strength = min(1.0, other_ab.strength + 0.05)
                    cross_protected += 1

        if is_parasitic:
            self._immune_memory[agent_id] += 1

        return {
            "response": response,
            "antibody_strength": round(antibodies[sig].strength, 4),
            "cross_protected": cross_protected,
            "total_antibodies": len(antibodies),
        }

    def check_immunity(self, agent_id: str, meme_payload: str) -> float:
        """How resistant is this agent to this specific meme? Returns 0-1."""
        sig = self._signature(meme_payload)
        ab = self._antibodies.get(agent_id, {}).get(sig)
        if not ab or not ab.is_effective:
            return 0.0
        return round(ab.strength, 4)

    def tick_decay(self) -> int:
        """Antibodies fade without reinforcement."""
        expired = 0
        for agent_id, antibodies in self._antibodies.items():
            dead_sigs = []
            for sig, ab in antibodies.items():
                ab.strength -= self.NATURAL_DECAY
                if ab.strength <= 0.0:
                    dead_sigs.append(sig)
                    expired += 1
            for sig in dead_sigs:
                del antibodies[sig]
        return expired

    def transfer_immunity(self, donor_id: str, recipient_id: str,
                          fraction: float = 0.3) -> int:
        """Share antibodies (e.g., through symbiosis). Returns count transferred."""
        donor_abs = self._antibodies.get(donor_id, {})
        transferred = 0
        for sig, ab in donor_abs.items():
            if ab.is_effective:
                recipient_abs = self._antibodies[recipient_id]
                if sig not in recipient_abs:
                    recipient_abs[sig] = Antibody(
                        signature=sig,
                        strength=ab.strength * fraction,
                        exposures=0, tick_created=self._tick,
                    )
                    transferred += 1
        return transferred

    @property
    def stats(self) -> dict[str, Any]:
        total_abs = sum(len(a) for a in self._antibodies.values())
        effective = sum(
            1 for a in self._antibodies.values()
            for ab in a.values() if ab.is_effective
        )
        return {
            "agents_with_immunity": len(self._antibodies),
            "total_antibodies": total_abs,
            "effective_antibodies": effective,
            "parasite_survivors": len(self._immune_memory),
        }
