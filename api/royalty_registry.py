"""Wave 135 — Royalty Registry.

Tracks royalties owed to workers and guilds whenever their artifacts
are resold or reused. Every lineage of a product records its
contributors, and resale events distribute a royalty share back to
them — creating passive income for the civilization's creators.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class RoyaltyAsset:
    """An artifact with a royalty-bearing contributor lineage."""

    def __init__(self, title: str, contributors: List[str]):
        self.title = title
        self.contributors = contributors
        self.resales = 0
        self.total_royalties = 0.0
        self.created = time.time()
        self.id = hashlib.sha256(f"royalty:{title}".encode()).hexdigest()[:10]

    def distribute(self, resale_price: float, share: float = 0.05) -> Dict[str, float]:
        if not self.contributors:
            return {}
        pot = resale_price * share
        split = pot / len(self.contributors)
        self.resales += 1
        self.total_royalties += pot
        return {c: round(split, 4) for c in self.contributors}

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "title": self.title, "contributors": self.contributors,
                "resales": self.resales, "royalties": round(self.total_royalties, 4)}


class RoyaltyRegistry:
    """Registry distributing resale royalties to creators."""

    def __init__(self):
        self._assets: Dict[str, RoyaltyAsset] = {}
        self._payouts: Dict[str, float] = {}

    def register(self, title: str, contributors: List[str]) -> RoyaltyAsset:
        asset = RoyaltyAsset(title, contributors)
        self._assets[asset.id] = asset
        return asset

    def resale(self, asset_id: str, resale_price: float, share: float = 0.05) -> Dict[str, float]:
        asset = self._assets.get(asset_id)
        if asset is None:
            return {}
        payouts = asset.distribute(resale_price, share)
        for creator, amount in payouts.items():
            self._payouts[creator] = self._payouts.get(creator, 0.0) + amount
        return payouts

    def balance(self, creator: str) -> float:
        return round(self._payouts.get(creator, 0.0), 4)

    def status(self) -> Dict[str, Any]:
        return {"assets": len(self._assets),
                "total_resales": sum(a.resales for a in self._assets.values()),
                "royalties_paid": round(sum(self._payouts.values()), 4)}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    registry = RoyaltyRegistry()
    return {"status": "active", "module": "royalty_registry",
            **registry.status()}
