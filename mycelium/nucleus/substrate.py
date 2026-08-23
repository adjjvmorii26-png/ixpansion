"""Resource substrate: the material laws beneath MYCELIUM."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class ResourceSite:
    """A nutrient site with a protected reserve and accumulated signal."""

    site_id: str
    position: tuple[float, float]
    nutrient: float = 10.0
    reserve: float = 2.0
    signal: float = 0.0

    def __post_init__(self) -> None:
        if self.nutrient < 0 or self.reserve < 0 or self.reserve > self.nutrient:
            raise ValueError("nutrient must be non-negative and reserve cannot exceed nutrient")
        if len(self.position) != 2:
            raise ValueError("position must be a two-dimensional coordinate")


@dataclass
class Substrate:
    """Owns sites and provides deterministic physical exchange operations."""

    sites: dict[str, ResourceSite] = field(default_factory=dict)

    def add_site(self, site: ResourceSite) -> ResourceSite:
        if site.site_id in self.sites:
            raise ValueError(f"site already exists: {site.site_id}")
        self.sites[site.site_id] = site
        return site

    def gradient(self, position: tuple[float, float]) -> dict[str, float]:
        """Return attraction strength from a coordinate to every living site."""
        gradients: dict[str, float] = {}
        for site_id, site in self.sites.items():
            distance = math.dist(position, site.position)
            proximity = 1.0 / (1.0 + distance)
            gradients[site_id] = round((site.nutrient + site.signal) * proximity, 8)
        return gradients

    def withdraw(self, site_id: str, amount: float) -> float:
        """Withdraw only unreserved nutrient; return the amount actually granted."""
        if site_id not in self.sites:
            raise KeyError(site_id)
        site = self.sites[site_id]
        available = max(0.0, site.nutrient - site.reserve)
        granted = max(0.0, min(amount, available))
        self.sites[site_id] = ResourceSite(
            site_id=site.site_id,
            position=site.position,
            nutrient=site.nutrient - granted,
            reserve=site.reserve,
            signal=site.signal,
        )
        return granted

    def deposit_signal(self, site_id: str, amount: float) -> float:
        """Leave a non-physical trace that can attract future hyphae."""
        if site_id not in self.sites:
            raise KeyError(site_id)
        if amount < 0:
            raise ValueError("signal deposits cannot be negative")
        old = self.sites[site_id]
        self.sites[site_id] = ResourceSite(
            site_id=old.site_id,
            position=old.position,
            nutrient=old.nutrient,
            reserve=old.reserve,
            signal=old.signal + amount,
        )
        return self.sites[site_id].signal

    @property
    def total_nutrient(self) -> float:
        return sum(site.nutrient for site in self.sites.values())

    def ordered_sites(self) -> Iterable[ResourceSite]:
        return sorted(self.sites.values(), key=lambda site: site.site_id)
