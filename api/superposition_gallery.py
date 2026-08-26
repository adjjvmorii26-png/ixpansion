"""Wave 123 — Superposition Gallery.

Exhibits artworks in superposition until observed — each piece exists
in multiple states simultaneously, and the act of viewing determines
which version manifests.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class SuperpositionArtwork:
    """An artwork existing in multiple states."""

    def __init__(self, title: str, states: List[str]):
        self.title = title
        self.possible_states = states
        self.current_state: Optional[str] = None
        self.observed_count = 0
        self.created = time.time()
        self.id = hashlib.sha256(f"art:{title}".encode()).hexdigest()[:10]

    def observe(self, observer_seed: int = 0) -> str:
        idx = observer_seed % len(self.possible_states)
        self.current_state = self.possible_states[idx]
        self.observed_count += 1
        return self.current_state

    def collapse(self) -> str:
        self.current_state = self.possible_states[0]
        self.observed_count += 1
        return self.current_state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "possible_states": len(self.possible_states),
            "current_state": self.current_state,
            "observed_count": self.observed_count,
        }


class SuperpositionGallery:
    """Gallery of artworks in superposition."""

    def __init__(self):
        self._artworks: List[SuperpositionArtwork] = []
        self._exhibitions: int = 0

    def exhibit(self, title: str, states: List[str]) -> SuperpositionArtwork:
        artwork = SuperpositionArtwork(title, states)
        self._artworks.append(artwork)
        return artwork

    def view(self, artwork_id: str, observer_seed: int = 0) -> Optional[str]:
        for art in self._artworks:
            if art.id == artwork_id:
                return art.observe(observer_seed)
        return None

    def collapse_all(self) -> int:
        collapsed = 0
        for art in self._artworks:
            if art.current_state is None:
                art.collapse()
                collapsed += 1
        self._exhibitions += 1
        return collapsed

    def get_artworks(self) -> List[Dict[str, Any]]:
        return [a.to_dict() for a in self._artworks]

    def status(self) -> Dict[str, Any]:
        return {
            "total_artworks": len(self._artworks),
            "exhibitions": self._exhibitions,
            "total_observations": sum(a.observed_count for a in self._artworks),
        }
