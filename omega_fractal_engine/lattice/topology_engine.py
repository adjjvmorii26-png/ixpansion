"""Manages shape-shifting worlds — routes between dimensional spaces."""
from __future__ import annotations

from typing import Any

from .dimensions.euclid.euclidean_space import EuclideanSpace
from .dimensions.non_euclid.non_euclidean_space import NonEuclideanSpace
from .dimensions.hyperbolic.hyperbolic_space import HyperbolicSpace


class TopologyEngine:
    def __init__(self) -> None:
        self._spaces: dict[str, Any] = {
            "euclid": EuclideanSpace(dims=3),
            "non_euclid": NonEuclideanSpace(dims=3, warp_factor=0.3),
            "hyperbolic": HyperbolicSpace(curvature=-1.0, max_radius=50),
        }
        self._active = "euclid"
        self._transition_log: list[dict[str, str]] = []

    @property
    def active_space(self) -> Any:
        return self._spaces[self._active]

    @property
    def active_name(self) -> str:
        return self._active

    def switch(self, target: str) -> bool:
        if target not in self._spaces:
            return False
        old = self._active
        self._active = target
        self._transition_log.append({"from": old, "to": target})
        return True

    def measure(self, a: tuple[float, ...], b: tuple[float, ...]) -> float:
        """Measure distance using the currently active space."""
        return self.active_space.distance(a, b)

    @property
    def available_spaces(self) -> list[str]:
        return list(self._spaces.keys())

    @property
    def transitions(self) -> list[dict[str, str]]:
        return self._transition_log[-20:]
