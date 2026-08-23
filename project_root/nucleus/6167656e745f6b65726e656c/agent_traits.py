"""Trait system — composable behavioral modifiers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


TRAIT_LIBRARY: dict[str, dict[str, Any]] = {
    "aggressive": {"attack_bonus": 0.3, "defense_penalty": 0.1},
    "defensive": {"defense_bonus": 0.25, "speed_penalty": 0.15},
    "explorer": {"vision_range": 2.0, "energy_cost_multiplier": 1.2},
    "social": {"cooperation_range": 3.0, "solo_penalty": 0.2},
    "efficient": {"energy_cost_multiplier": 0.8},
    "resilient": {"max_energy_bonus": 20.0},
    "adaptive": {"mutation_tolerance": 0.4},
}


@dataclass
class TraitSet:
    active: set[str] = field(default_factory=set)
    _modifiers: dict[str, float] = field(default_factory=dict)

    def add(self, trait_name: str) -> bool:
        if trait_name not in TRAIT_LIBRARY or trait_name in self.active:
            return False
        self.active.add(trait_name)
        for key, val in TRAIT_LIBRARY[trait_name].items():
            self._modifiers[key] = self._modifiers.get(key, 0) + val
        return True

    def get_modifier(self, key: str, default: float = 0.0) -> float:
        return self._modifiers.get(key, default)

    @property
    def summary(self) -> dict[str, Any]:
        return {"traits": sorted(self.active), "modifiers": {k: round(v, 3) for k, v in self._modifiers.items()}}
