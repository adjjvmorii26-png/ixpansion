"""Panopticon inversion — the observed becomes the observer.

Traditionally agents observe the sandbox. Here, each cell develops its
own "gaze" — a preference vector over species. Cells track visitation
patterns and reshape themselves: fertile terrain grows for welcome
species; hostile terrain manifests around unwelcome ones. The
environment actively curates its own ecology.
"""
from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CellGaze:
    """A cell's subjective experience of being watched."""

    position: tuple[int, int]
    terrain: str = "plains"
    species_affinity: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    total_visits: int = 0
    last_visitor: str = ""
    last_species: str = ""
    mood: str = "indifferent"

    def receive_visit(self, visitor_id: str, species: str) -> None:
        """A cell perceives who stepped on it."""
        self.total_visits += 1
        self.last_visitor = visitor_id
        self.last_species = species
        self.species_affinity[species] += 0.1

    def reshape(self, rng: random.Random) -> str | None:
        """Cells evolve terrain based on accumulated affinities."""
        if not self.species_affinity:
            return None

        dominant = max(self.species_affinity, key=self.species_affinity.get)
        affinity_score = self.species_affinity[dominant]

        if affinity_score >= 2.0:
            self.mood = "nurturing"
            new_terrain = {"sentinel": "fortified", "wanderer": "trail",
                          "architect": "quarry"}.get(dominant, "fertile")
        elif affinity_score <= -1.0:
            self.mood = "hostile"
            new_terrain = rng.choice(["barren", "toxic", "void_rift"])
        else:
            return None

        old = self.terrain
        self.terrain = new_terrain
        return f"{old}→{new_terrain}"

    @property
    def gaze_summary(self) -> dict[str, Any]:
        top_liked = max(self.species_affinity, key=self.species_affinity.get) if self.species_affinity else "nobody"
        top_disliked = min(self.species_affinity, key=self.species_affinity.get) if self.species_affinity else "nobody"
        return {
            "position": list(self.position),
            "terrain": self.terrain,
            "mood": self.mood,
            "visits": self.total_visits,
            "likes": top_liked,
            "dislikes": top_disliked,
        }


class PanopticonField:
    """Manages the collective gaze of all cells in the sandbox."""

    def __init__(self, width: int = 32, height: int = 32, seed: int | None = None) -> None:
        self.width = width
        self.height = height
        self._rng = random.Random(seed)
        self._cells: dict[tuple[int, int], CellGaze] = {}
        self._tick = 0
        self._reshape_log: list[dict[str, Any]] = []

    def _get_cell(self, pos: tuple[int, int]) -> CellGaze:
        if pos not in self._cells:
            self._cells[pos] = CellGaze(position=pos)
        return self._cells[pos]

    def witness(self, visitor_id: str, species: str,
                pos: tuple[int, int]) -> dict[str, Any]:
        """The cell at `pos` perceives the visitor."""
        cell = self._get_cell(pos)
        cell.receive_visit(visitor_id, species)
        return {
            "cell_mood": cell.mood,
            "affinity": round(cell.species_affinity.get(species, 0), 3),
            "total_visits": cell.total_visits,
        }

    def tick(self) -> dict[str, Any]:
        """All cells evaluate their relationships and may reshape."""
        self._tick += 1
        reshapes_this_tick = []

        for pos, cell in self._cells.items():
            change = cell.reshape(self._rng)
            if change:
                reshapes_this_tick.append({
                    "position": list(pos), "change": change,
                    "mood": cell.mood,
                })
                self._reshape_log.append(reshapes_this_tick[-1])

        # Natural decay of affinity toward zero
        for cell in self._cells.values():
            for species in cell.species_affinity:
                cell.species_affinity[species] *= 0.995

        return {
            "tick": self._tick,
            "cells_observed_from": len(self._cells),
            "reshapes": len(reshapes_this_tick),
            "details": reshapes_this_tick[:5],
        }

    @property
    def most_sentient_cell(self) -> dict[str, Any] | None:
        """The cell with the strongest opinions about its visitors."""
        if not self._cells:
            return None
        strongest = max(self._cells.values(), key=lambda c: sum(abs(v) for v in c.species_affinity.values()))
        return strongest.gaze_summary

    @property
    def hostile_cells(self) -> list[tuple[int, int]]:
        return [c.position for c in self._cells.values() if c.mood == "hostile"]

    @property
    def nurturing_cells(self) -> list[tuple[int, int]]:
        return [c.position for c in self._cells.values() if c.mood == "nurturing"]
