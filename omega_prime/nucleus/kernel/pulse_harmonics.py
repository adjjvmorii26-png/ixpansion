"""Pulse harmonics — emergent agent synchronization.

Each agent carries a phase oscillator. When multiple agents' phases
align, their combined action produces constructive interference
(amplified effect). Misaligned phases cause destructive interference
(cancelled or weakened actions). Agents naturally drift toward sync
through Kuramoto-style coupling — no central coordinator needed.

This creates emergent "rituals" where agents must coordinate timing
to achieve effects greater than the sum of individual actions.
"""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Oscillator:
    phase: float = 0.0          # radians, 0 to 2π
    natural_freq: float = 1.0   # intrinsic frequency
    coupling_strength: float = 0.3

    def advance(self, dt: float = 0.1) -> None:
        """Free-run one step."""
        self.phase = (self.phase + self.natural_freq * dt) % (2 * math.pi)

    def couple(self, neighbor_phase: float) -> float:
        """Kuramoto coupling: pull toward neighbor's phase."""
        return self.coupling_strength * math.sin(neighbor_phase - self.phase)


class PulseHarmonics:
    def __init__(self, kuramoto_k: float = 0.5) -> None:
        self._oscillators: dict[str, Oscillator] = {}
        self._kuramoto_k = kuramoto_k
        self._tick = 0
        self._interference_log: list[dict[str, Any]] = []

    def enroll(self, agent_id: str, freq: float | None = None) -> None:
        import random
        self._oscillators[agent_id] = Oscillator(
            phase=random.uniform(0, 2 * math.pi),
            natural_freq=freq if freq else random.uniform(0.8, 1.2),
        )

    def tick(self) -> dict[str, Any]:
        """Advance all oscillators with mutual coupling."""
        ids = list(self._oscillators.keys())
        if len(ids) < 2:
            for osc in self._oscillators.values():
                osc.advance()
            self._tick += 1
            return {"tick": self._tick, "order": self.order_parameter}

        # Compute coupling adjustments
        new_phases = {}
        for aid in ids:
            osc = self._oscillators[aid]
            coupling_sum = sum(
                osc.couple(self._oscillators[other].phase)
                for other in ids if other != aid
            )
            avg_coupling = coupling_sum / max(len(ids) - 1, 1)
            new_phase = (osc.phase + (osc.natural_freq + self._kuramoto_k * avg_coupling) * 0.1) % (2 * math.pi)
            new_phases[aid] = new_phase

        for aid, phase in new_phases.items():
            self._oscillators[aid].phase = phase

        self._tick += 1
        return {"tick": self._tick, "order": self.order_parameter}

    @property
    def order_parameter(self) -> float:
        """Kuramoto order parameter r: 0=fully desynced, 1=perfectly synced."""
        n = len(self._oscillators)
        if n == 0:
            return 0.0
        real_sum = sum(math.cos(o.phase) for o in self._oscillators.values())
        imag_sum = sum(math.sin(o.phase) for o in self._oscillators.values())
        return round(math.hypot(real_sum, imag_sum) / n, 6)

    def combine_actions(self, actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Resolve interference between simultaneous actions from synced/desynced agents."""
        if len(actions) < 2:
            return actions

        result = []
        used = set()

        for i, a in enumerate(actions):
            if i in used:
                continue
            aid_a = a.get("agent_id", "")
            osc_a = self._oscillators.get(aid_a)
            if not osc_a:
                result.append(a)
                used.add(i)
                continue

            # Find best-matching partner
            best_j = None
            best_alignment = -2.0
            for j in range(i + 1, len(actions)):
                if j in used:
                    continue
                aid_b = actions[j].get("agent_id", "")
                osc_b = self._oscillators.get(aid_b)
                if not osc_b:
                    continue
                alignment = math.cos(osc_a.phase - osc_b.phase)  # 1=in-phase, -1=anti-phase
                if alignment > best_alignment:
                    best_alignment = alignment
                    best_j = j

            if best_j is not None and best_alignment > 0.7:
                # Constructive interference: amplify both actions
                b = actions[best_j]
                amplified = {
                    **a,
                    "amplified": True,
                    "interference": round(best_alignment, 4),
                    "partner": b.get("agent_id", ""),
                    "power_boost": round(1.0 + best_alignment, 3),
                }
                result.append(amplified)
                used.add(i)
                used.add(best_j)
                self._interference_log.append({"tick": self._tick, "type": "constructive", "alignment": round(best_alignment, 4)})
            elif best_j is not None and best_alignment < -0.7:
                # Destructive interference: cancel both
                used.add(i)
                used.add(best_j)
                self._interference_log.append({"tick": self._tick, "type": "destructive", "alignment": round(best_alignment, 4)})
            else:
                result.append(a)
                used.add(i)

        return result

    @property
    def phases(self) -> dict[str, float]:
        return {aid: round(o.phase, 4) for aid, o in self._oscillators.items()}

    @property
    def is_synchronized(self) -> bool:
        return self.order_parameter > 0.8

    @property
    def recent_interference(self) -> list[dict[str, Any]]:
        return self._interference_log[-10:]
