"""Agents merge into super-forms when conditions align."""
from __future__ import annotations

from typing import Any


class ConvergenceRitual:
    def __init__(self) -> None:
        self._threshold = 0.7  # Phase alignment needed

    def attempt_merge(self, agents: list[dict[str, Any]],
                      phase_alignments: dict[str, float]) -> dict[str, Any] | None:
        """Attempt to merge agents into a single super-form."""
        if len(agents) < 2:
            return None

        # Check if enough agents are sufficiently aligned
        aligned = [
            a for a in agents
            if phase_alignments.get(a.get("id", ""), 0) >= self._threshold
        ]

        if len(aligned) < 2:
            return None

        merged_genome: dict[str, float] = {}
        for agent in aligned:
            for key, val in agent.get("genome", {}).items():
                merged_genome[key] = max(merged_genome.get(key, 0), val)

        return {
            "form": f"super-{'-'.join(a.get('species', '?')[:3] for a in aligned)}",
            "participants": [a.get("id") for a in aligned],
            "genome": merged_genome,
            "power_multiplier": round(len(aligned) ** 1.5, 2),
        }
