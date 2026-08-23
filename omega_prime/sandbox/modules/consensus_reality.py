"""Consensus reality protocol.

When multiple agents observe the same spatial cell, their individual
perceptions are compared. If a supermajority agrees, the observation
"collapses" into objective reality. If agents disagree, the cell enters
quantum ambiguity — all claimed states coexist until resolved.

This creates an epistemological game: agents can lie about observations
to manipulate shared reality.
"""
from __future__ import annotations

import hashlib
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class CellState(Enum):
    UNOBSERVED = auto()
    AMBIGUOUS = auto()      # Disagreement — multiple realities coexist
    CONSOLIDATED = auto()   # Consensus reached — single truth
    CONTESTED = auto()      # Active dispute — no resolution possible yet


@dataclass
class Observation:
    observer_id: str
    species: str
    claimed_content: str
    confidence: float
    tick: int

    @property
    def weight(self) -> float:
        """Trustworthiness of this observation."""
        return max(0.0, min(1.0, self.confidence))


@dataclass
class Cell:
    position: tuple[int, int]
    state: CellState = CellState.UNOBSERVED
    observations: list[Observation] = field(default_factory=list)
    consolidated_truth: str | None = None
    ambiguity_set: set[str] = field(default_factory=set)
    last_resolved_tick: int = -1

    @property
    def is_observed(self) -> bool:
        return len(self.observations) > 0


class ConsensusReality:
    SUPERMAJORITY_THRESHOLD = 0.6  # Fraction of observers needed for consensus
    MIN_OBSERVERS = 2              # Minimum observers to trigger consolidation

    def __init__(self) -> None:
        self._cells: dict[tuple[int, int], Cell] = {}
        self._agent_credibility: dict[str, float] = defaultdict(lambda: 0.5)
        self._tick = 0

    def submit_observation(self, observer_id: str, species: str,
                           position: tuple[int, int],
                           content: str, confidence: float) -> dict[str, Any]:
        """Submit an agent's claim about what exists at a position."""
        self._tick += 1
        if position not in self._cells:
            self._cells[position] = Cell(position=position)

        obs = Observation(
            observer_id=observer_id,
            species=species,
            claimed_content=content,
            confidence=max(0.0, min(1.0, confidence)),
            tick=self._tick,
        )
        cell = self._cells[position]
        cell.observations.append(obs)

        result = self._evaluate(cell)
        return {
            "position": position,
            "state": cell.state.name,
            "truth": cell.consolidated_truth,
            "ambiguity": sorted(cell.ambiguity_set) if cell.ambiguity_set else [],
            "observers": len(cell.observations),
            "credibility_shift": self._update_credibility(cell),
        }

    def _evaluate(self, cell: Cell) -> None:
        """Determine whether a cell reaches consensus or stays ambiguous."""
        if len(cell.observations) < self.MIN_OBSERVERS:
            cell.state = CellState.UNOBSERVED
            return

        # Weighted vote
        votes: Counter[str] = Counter()
        for obs in cell.observations:
            credibility = self._agent_credibility.get(obs.observer_id, 0.5)
            effective_weight = obs.weight * credibility
            votes[obs.claimed_content] += effective_weight

        total_weight = sum(votes.values())
        if total_weight == 0:
            cell.state = CellState.CONTESTED
            return

        winner, winner_votes = votes.most_common(1)[0]
        winner_fraction = winner_votes / total_weight

        if winner_fraction >= self.SUPERMAJORITY_THRESHOLD:
            cell.state = CellState.CONSOLIDATED
            cell.consolidated_truth = winner
            cell.ambiguity_set.clear()
        else:
            cell.state = CellState.AMBIGUOUS
            cell.ambiguity_set = {content for content, count in votes.items() if count > 0}
            cell.consolidated_truth = None

    def _update_credibility(self, cell: Cell) -> dict[str, float]:
        """Adjust agent credibility based on whether they agreed with consensus."""
        shifts = {}
        if cell.state != CellState.CONSOLIDATED or not cell.consolidated_truth:
            return shifts

        for obs in cell.observations:
            old = self._agent_credibility[obs.observer_id]
            if obs.claimed_content == cell.consolidated_truth:
                shift = +0.02 * obs.confidence
            else:
                shift = -0.03
            self._agent_credibility[obs.observer_id] = max(0.0, min(1.0, old + shift))
            shifts[obs.observer_id] = round(shift, 4)

        return shifts

    def get_perceived(self, position: tuple[int, int]) -> list[str]:
        """What does an agent perceive at this position? Returns all possible realities."""
        cell = self._cells.get(position)
        if not cell or not cell.is_observed:
            return []
        if cell.state == CellState.CONSOLIDATED:
            return [cell.consolidated_truth]
        return sorted(cell.ambiguity_set)

    def force_consolidate(self, position: tuple[int, int], truth: str) -> bool:
        """Admin override — forcibly set truth. Use sparingly."""
        if position in self._cells:
            cell = self._cells[position]
            cell.state = CellState.CONSOLIDATED
            cell.consolidated_truth = truth
            cell.ambiguity_set.clear()
            return True
        return False

    @property
    def stats(self) -> dict[str, Any]:
        states = Counter(c.state.name for c in self._cells.values())
        credible_agents = [a for a, c in self._agent_credibility.items() if c >= 0.7]
        return {
            "total_cells": len(self._cells),
            "states": dict(states),
            "credible_agents": len(credible_agents),
            "avg_credibility": round(
                sum(self._agent_credibility.values()) / max(len(self._agent_credibility), 1), 4
            ),
        }
