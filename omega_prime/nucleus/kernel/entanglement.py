"""Quantum entanglement network.

Two agents can form an entangled pair. Once entangled, certain
measurements on one agent instantly determine correlated properties
of the other — regardless of spatial separation. Entanglement decays
over time or through decoherence (too many measurements).

This creates strategic depth: agents can share fate, transfer states,
and coordinate without communication by exploiting Bell correlations.
"""
from __future__ import annotations

import hashlib
import random
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class BellState(Enum):
    PHI_PLUS = auto()    # |00⟩ + |11⟩ — same outcome
    PHI_MINUS = auto()   # |00⟩ − |11⟩ — same outcome, opposite phase
    PSI_PLUS = auto()    # |01⟩ + |10⟩ — opposite outcome
    PSI_MINUS = auto()   # |01⟩ − |10⟩ — anti-correlated


@dataclass
class EntangledPair:
    pair_id: str
    agent_a: str
    agent_b: str
    bell_state: BellState
    coherence: float = 1.0   # 1=fully entangled, 0=decohered

    @property
    def is_active(self) -> bool:
        return self.coherence > 0.05

    @property
    def are_anticorrelated(self) -> bool:
        return self.bell_state in (BellState.PSI_PLUS, BellState.PSI_MINUS)

    def decohere(self, rate: float) -> None:
        self.coherence = max(0.0, self.coherence - rate)


@dataclass
class MeasurementResult:
    measured_agent: str
    remote_agent: str
    local_value: Any
    remote_value: Any
    correlation: float  # How strongly results were correlated
    coherence_at_measurement: float


class EntanglementNetwork:
    DECOHERENCE_PER_MEASUREMENT = 0.15
    NATURAL_DECAY_RATE = 0.01

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._pairs: dict[str, EntangledPair] = {}
        self._agent_to_pair: dict[str, str] = {}

    def entangle(self, agent_a: str, agent_b: str,
                 bell_state: BellState = BellState.PHI_PLUS) -> dict[str, Any]:
        if agent_a in self._agent_to_pair or agent_b in self._agent_to_pair:
            return {"success": False, "reason": "already_entangled"}

        pid = hashlib.sha256(f"{agent_a}:{agent_b}:{bell_state.name}".encode()).hexdigest()[:12]
        pair = EntangledPair(pair_id=pid, agent_a=agent_a, agent_b=agent_b, bell_state=bell_state)
        self._pairs[pid] = pair
        self._agent_to_pair[agent_a] = pid
        self._agent_to_pair[agent_b] = pid

        return {
            "success": True, "pair_id": pid[:8],
            "bell_state": bell_state.name,
            "anticorrelated": pair.are_anticorrelated,
        }

    def measure(self, agent_id: str, observable: str,
                value: Any) -> MeasurementResult | None:
        """Measure one agent; instantly determine the partner's correlated value."""
        pid = self._agent_to_pair.get(agent_id)
        if not pid:
            return None
        pair = self._pairs.get(pid)
        if not pair or not pair.is_active:
            return None

        other = pair.agent_b if agent_id == pair.agent_a else pair.agent_a

        # Determine remote value based on Bell state
        if pair.are_anticorrelated:
            if isinstance(value, bool):
                remote_value = not value
            elif isinstance(value, (int, float)):
                remote_value = -value
            elif isinstance(value, str):
                remote_value = f"NOT({value})"
            else:
                remote_value = value
        else:
            remote_value = value  # Perfect correlation

        correlation = pair.coherence
        pair.decohere(self.DECOHERENCE_PER_MEASUREMENT)

        return MeasurementResult(
            measured_agent=agent_id,
            remote_agent=other,
            local_value=value,
            remote_value=remote_value,
            correlation=round(correlation, 4),
            coherence_at_measurement=round(pair.coherence, 4),
        )

    def tick_decay(self) -> int:
        """Natural decoherence over time."""
        dead_pairs = []
        for pid, pair in self._pairs.items():
            pair.decohere(self.NATURAL_DECAY_RATE)
            if not pair.is_active:
                dead_pairs.append(pid)
        for pid in dead_pairs:
            pair = self._pairs.pop(pid)
            self._agent_to_pair.pop(pair.agent_a, None)
            self._agent_to_pair.pop(pair.agent_b, None)
        return len(dead_pairs)

    def disentangle(self, agent_id: str) -> bool:
        """Voluntarily break an entanglement."""
        pid = self._agent_to_pair.pop(agent_id, None)
        if not pid:
            return False
        pair = self._pairs.pop(pid, None)
        if pair:
            other = pair.agent_b if agent_id == pair.agent_a else pair.agent_a
            self._agent_to_pair.pop(other, None)
        return True

    @property
    def active_entanglements(self) -> list[dict[str, Any]]:
        return [
            {"pair": p.pair_id[:8], "agents": [p.agent_a, p.agent_b],
             "bell_state": p.bell_state.name, "coherence": round(p.coherence, 4)}
            for p in self._pairs.values() if p.is_active
        ]

    @property
    def stats(self) -> dict[str, Any]:
        active = [p for p in self._pairs.values() if p.is_active]
        avg_coherence = sum(p.coherence for p in active) / max(len(active), 1)
        anticorr = sum(1 for p in active if p.are_anticorrelated)
        return {
            "active_pairs": len(active),
            "avg_coherence": round(avg_coherence, 4),
            "anti_correlated_pairs": anticorr,
            "entangled_agents": len(self._agent_to_pair),
        }
