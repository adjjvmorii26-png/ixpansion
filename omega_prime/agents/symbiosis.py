"""Symbiosis protocol for cross-species capability sharing.

Two agents of different species can form a temporary symbiotic bond.
The bond merges their observation scopes and grants access to each
other's species-specific abilities — at the cost of coupled fate:
if either partner's entropy hits lockout, both suffer degraded capacity.

Bonds have a natural half-life and dissolve if not renewed.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class BondState(Enum):
    FORMING = auto()
    ACTIVE = auto()
    DECAYING = auto()
    DISSOLVED = auto()


@dataclass
class SymbioticBond:
    bond_id: str
    agent_a: str
    agent_b: str
    species_a: str
    species_b: str
    strength: float = 1.0
    formed_at: float = field(default_factory=time.monotonic)
    state: BondState = BondState.FORMING

    def __post_init__(self) -> None:
        self.state = BondState.ACTIVE

    @property
    def partners(self) -> tuple[str, str]:
        return (self.agent_a, self.agent_b)

    @property
    def shared_capabilities(self) -> list[str]:
        """Capabilities that emerge only from this pairing."""
        caps: list[str] = []
        combo = {self.species_a, self.species_b}
        if combo == {"sentinel", "wanderer"}:
            caps = ["threat_aware_navigation", "safe_exploration"]
        elif combo == {"architect", "sentinel"}:
            caps = ["fortified_construction", "defensive_planning"]
        elif combo == {"architect", "wanderer"}:
            caps = ["reconnaissance_mapping", "infrastructure_scouting"]
        else:
            caps = ["generic_coordination"]
        return caps


class SymbiosisManager:
    def __init__(self) -> None:
        self._bonds: dict[str, SymbioticBond] = {}
        self._agent_index: dict[str, str] = {}  # agent_id -> bond_id
        self._counter = 0

    def propose(self, agent_a_id: str, agent_a_species: str,
                agent_b_id: str, agent_b_species: str) -> SymbioticBond | None:
        """Attempt to form a bond between two different-species agents."""
        if agent_a_species == agent_b_species:
            return None
        if agent_a_id in self._agent_index or agent_b_id in self._agent_index:
            return None

        self._counter += 1
        bond = SymbioticBond(
            bond_id=f"bond_{self._counter}",
            agent_a=agent_a_id,
            agent_b=agent_b_id,
            species_a=agent_a_species,
            species_b=agent_b_species,
        )
        self._bonds[bond.bond_id] = bond
        self._agent_index[agent_a_id] = bond.bond_id
        self._agent_index[agent_b_id] = bond.bond_id
        return bond

    def tick(self, decay_rate: float = 0.02) -> list[str]:
        """Decay all bonds. Returns IDs of dissolved bonds."""
        dissolved = []
        for bid, bond in self._bonds.items():
            bond.strength -= decay_rate
            if bond.strength <= 0.0:
                bond.state = BondState.DISSOLVED
                dissolved.append(bid)
                self._agent_index.pop(bond.agent_a, None)
                self._agent_index.pop(bond.agent_b, None)
            elif bond.strength < 0.3:
                bond.state = BondState.DECAYING

        for bid in dissolved:
            del self._bonds[bid]
        return dissolved

    def get_partner(self, agent_id: str) -> str | None:
        """Return the bonded partner of an agent."""
        bid = self._agent_index.get(agent_id)
        if not bid:
            return None
        bond = self._bonds.get(bid)
        if not bond:
            return None
        if bond.agent_a == agent_id:
            return bond.agent_b
        return bond.agent_a

    def get_shared_capabilities(self, agent_id: str) -> list[str]:
        """Get emergent capabilities available to a bonded agent."""
        bid = self._agent_index.get(agent_id)
        if not bid or bid not in self._bonds:
            return []
        return self._bonds[bid].shared_capabilities

    @property
    def active_bonds(self) -> list[SymbioticBond]:
        return [b for b in self._bonds.values() if b.state == BondState.ACTIVE]
