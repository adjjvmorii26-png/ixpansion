"""Emergent cartography — subjective mental maps built through exploration.

Agents don't receive ground-truth maps. They build their own by exploring,
and their maps are imperfect: unvisited cells are blank, visited cells may
be misremembered (memory distortion), and terrain types can be confused.

When agents share maps, the receiving agent merges the donor's knowledge
with its own — including any errors. This creates collaborative knowledge
that's more complete but potentially less accurate than individual maps.
"""
from __future__ import annotations

import random
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


TERRAIN_TYPES = ["plains", "forest", "rock", "water", "void", "crystal"]
CONFUSION_MATRIX = {
    "plains": ["forest", "rock"],
    "forest": ["plains", "crystal"],
    "rock": ["plains", "void"],
    "water": ["void", "crystal"],
    "void": ["rock", "water"],
    "crystal": ["forest", "water"],
}


@dataclass
class MapCell:
    """An agent's belief about a single cell."""

    position: tuple[int, int]
    believed_terrain: str
    confidence: float = 0.5     # How sure they are
    visit_count: int = 0
    last_visited_tick: int = 0
    source: str = "personal"    # personal, shared, inherited


class AgentMap:
    """A single agent's subjective map of the world."""

    def __init__(self, owner_id: str, seed: int | None = None) -> None:
        self.owner_id = owner_id
        self._cells: dict[tuple[int, int], MapCell] = {}
        self._rng = random.Random(seed)

    @property
    def explored_count(self) -> int:
        return len(self._cells)

    @property
    def coverage(self) -> float:
        """Fraction of the world this agent has mapped."""
        return min(1.0, len(self._cells) / 100)  # Assume ~100 cells in world

    def explore(self, pos: tuple[int, int], actual_terrain: str, tick: int) -> MapCell:
        """Visit a cell; perceive it with possible error."""
        perceived = actual_terrain

        # Memory distortion: chance of misidentifying terrain
        if self._rng.random() < 0.15:
            confusions = CONFUSION_MATRIX.get(actual_terrain, [actual_terrain])
            perceived = self._rng.choice(confusions)

        existing = self._cells.get(pos)
        if existing:
            # Revisiting increases confidence; may correct previous error
            existing.visit_count += 1
            existing.last_visited_tick = tick
            if existing.believed_terrain != actual_terrain:
                # Correction with higher confidence on repeat visits
                if self._rng.random() < 0.6 + existing.visit_count * 0.1:
                    existing.believed_terrain = actual_terrain
                    existing.confidence = min(1.0, existing.confidence + 0.15)
            else:
                existing.confidence = min(1.0, existing.confidence + 0.1)
            return existing

        cell = MapCell(
            position=pos, believed_terrain=perceived,
            confidence=self._rng.uniform(0.4, 0.7),
            visit_count=1, last_visited_tick=tick,
        )
        self._cells[pos] = cell
        return cell

    def share_with(self, recipient: "AgentMap", overlap_bonus: float = 0.1) -> int:
        """Merge this map into recipient's map. Returns cells transferred."""
        transferred = 0
        for pos, my_cell in self._cells.items():
            their_cell = recipient._cells.get(pos)
            if not their_cell:
                # Recipient learns new area
                recipient._cells[pos] = MapCell(
                    position=pos, believed_terrain=my_cell.believed_terrain,
                    confidence=my_cell.confidence * 0.8,  # Second-hand info less trusted
                    visit_count=0, source=f"shared_from_{self.owner_id[:8]}",
                )
                transferred += 1
            elif my_cell.confidence > their_cell.confidence:
                # Donor has better information; update
                if my_cell.believed_terrain != their_cell.believed_terrain:
                    their_cell.believed_terrain = my_cell.believed_terrain
                    their_cell.confidence = my_cell.confidence * 0.9
                    their_cell.source = f"corrected_by_{self.owner_id[:8]}"
                transferred += 1

        return transferred

    def get_belief(self, pos: tuple[int, int]) -> MapCell | None:
        return self._cells.get(pos)

    @property
    def accuracy_summary(self) -> dict[str, Any]:
        terrains = defaultdict(int)
        sources = defaultdict(int)
        for c in self._cells.values():
            terrains[c.believed_terrain] += 1
            sources[c.source.split("_")[0]] += 1
        avg_conf = sum(c.confidence for c in self._cells.values()) / max(len(self._cells), 1)
        return {
            "explored": len(self._cells),
            "avg_confidence": round(avg_conf, 3),
            "terrain_distribution": dict(terrains),
            "info_sources": dict(sources),
        }


class CartographyNetwork:
    def __init__(self, world_size: int = 10, seed: int | None = None) -> None:
        self.world_size = world_size
        self._ground_truth: dict[tuple[int, int], str] = {}
        self._maps: dict[str, AgentMap] = {}
        self._rng = random.Random(seed)
        self._tick = 0
        self._generate_world()

    def _generate_world(self) -> None:
        for x in range(self.world_size):
            for y in range(self.world_size):
                self._ground_truth[(x, y)] = self._rng.choice(TERRAIN_TYPES)

    def register_agent(self, agent_id: str) -> AgentMap:
        amap = AgentMap(agent_id, seed=hash(agent_id) % 2**32)
        self._maps[agent_id] = amap
        return amap

    def explore_at(self, agent_id: str, pos: tuple[int, int]) -> MapCell:
        """Agent visits a cell and perceives it."""
        amap = self._get_map(agent_id)
        actual = self._ground_truth.get(pos, "unknown")
        self._tick += 1
        return amap.explore(pos, actual, self._tick)

    def share_maps(self, from_agent: str, to_agent: str) -> int:
        """Transfer map knowledge between two agents."""
        donor = self._get_map(from_agent)
        recipient = self._get_map(to_agent)
        return donor.share_with(recipient)

    def check_accuracy(self, agent_id: str) -> dict[str, Any]:
        """How accurate is this agent's map compared to ground truth?"""
        amap = self._get_map(agent_id)
        correct = 0
        total = 0
        errors_by_type = defaultdict(int)

        for pos, cell in amap._cells.items():
            actual = self._ground_truth.get(pos)
            if actual is None:
                continue
            total += 1
            if cell.believed_terrain == actual:
                correct += 1
            else:
                errors_by_type[f"{actual}→{cell.believed_terrain}"] += 1

        accuracy = correct / max(total, 1)
        return {
            "accuracy": round(accuracy, 4),
            "cells_checked": total,
            "errors": dict(errors_by_type),
        }

    def _get_map(self, agent_id: str) -> AgentMap:
        if agent_id not in self._maps:
            return self.register_agent(agent_id)
        return self._maps[agent_id]

    @property
    def stats(self) -> dict[str, Any]:
        total_explored = sum(m.explored_count for m in self._maps.values())
        return {
            "agents_mapping": len(self._maps),
            "total_explorations": total_explored,
            "world_cells": len(self._ground_truth),
            "tick": self._tick,
        }
