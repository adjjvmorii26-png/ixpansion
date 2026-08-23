"""Reality fabric — mutable physics layer.

Agents can spend entropy to overwrite local physics rules within a
spatial region. Each "weave" creates a law patch that overrides
global defaults for agents standing inside it. Law patches decay
over time unless reinforced, creating contested territories.

This is the meta-game: agents fight not just for territory but for
the right to define what "territory" means.
"""
from __future__ import annotations

import hashlib
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class LawType(Enum):
    GRAVITY = auto()
    TIME_FLOW = auto()
    FRICTION = auto()
    ENTROPY_COST = auto()
    VISIBILITY = auto()
    COMMUNICATION = auto()


@dataclass
class LawPatch:
    patch_id: str
    center: tuple[float, float]
    radius: float
    laws: dict[str, Any]
    strength: float  # 1.0 = full authority
    weaver_id: str
    tick_woven: int

    def contains(self, pos: tuple[float, float]) -> bool:
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        return (dx ** 2 + dy ** 2) <= (self.radius ** 2)

    def erode(self, rate: float = 0.01) -> None:
        self.strength = max(0.0, self.strength - rate)


class RealityFabric:
    """Manages overlapping law patches with priority resolution."""

    GLOBAL_DEFAULTS = {
        "gravity": -9.81,
        "time_multiplier": 1.0,
        "friction": 0.98,
        "entropy_modifier": 1.0,
        "visibility_range": 10.0,
        "can_communicate": True,
    }

    def __init__(self) -> None:
        self._patches: dict[str, LawPatch] = {}
        self._tick = 0

    def weave(self, weaver_id: str, position: tuple[float, float],
              radius: float, laws: dict[str, Any], tick: int) -> str | None:
        """Attempt to weave a new law patch. Returns patch_id or None if rejected."""
        # Validate laws
        valid_keys = {lt.name.lower() for lt in LawType}
        filtered = {k: v for k, v in laws.items() if k in valid_keys}
        if not filtered:
            return None

        pid = hashlib.sha256(f"{weaver_id}:{position}:{tick}".encode()).hexdigest()[:12]

        # Check for conflicting patches at same location
        for existing in self._patches.values():
            if existing.contains(position) and existing.weaver_id != weaver_id:
                # Contest: weaker existing patch gets overwritten
                if existing.strength < 0.3:
                    del self._patches[existing.patch_id]
                else:
                    return None  # Cannot overpower a strong patch

        patch = LawPatch(
            patch_id=pid, center=position, radius=radius,
            laws=filtered, strength=1.0, weaver_id=weaver_id, tick_woven=tick,
        )
        self._patches[pid] = patch
        return pid

    def resolve_physics(self, position: tuple[float, float]) -> dict[str, Any]:
        """Get effective physics at a position (patched or global)."""
        result = dict(self.GLOBAL_DEFAULTS)
        applicable = [p for p in self._patches.values()
                      if p.contains(position) and p.strength > 0.0]
        applicable.sort(key=lambda p: p.strength)
        for patch in applicable:
            result.update(patch.laws)
            result["_governed_by"] = patch.weaver_id
        return result

    def reinforce(self, patch_id: str, amount: float) -> bool:
        if patch_id in self._patches:
            self._patches[patch_id].strength = min(1.0, self._patches[patch_id].strength + amount)
            return True
        return False

    def tick(self) -> None:
        self._tick += 1
        expired = []
        for pid, patch in self._patches.items():
            patch.erode(rate=0.005)
            if patch.strength <= 0.0:
                expired.append(pid)
        for pid in expired:
            del self._patches[pid]

    @property
    def active_patches(self) -> list[dict[str, Any]]:
        return [
            {"id": p.patch_id, "weaver": p.weaver_id, "laws": p.laws,
             "strength": round(p.strength, 3), "radius": p.radius}
            for p in self._patches.values()
        ]

    @property
    def contested_zones(self) -> list[str]:
        return [p.patch_id for p in self._patches.values() if p.strength < 0.5]
