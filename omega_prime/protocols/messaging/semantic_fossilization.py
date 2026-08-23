"""Semantic fossilization — dead words become etymological strata.

When words fall out of use, they don't disappear — they fossilize.
Fossilized words retain their original meaning compressed into a
dense form. Future agents who excavate these fossils can recover
ancient concepts and potentially revive them.

This creates linguistic archaeology: the deeper you dig into the
vocabulary's history, the more archaic (and potentially powerful)
the concepts you find.
"""
from __future__ import annotations

import hashlib
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SemanticFossil:
    """A compressed remnant of a dead word."""

    fossil_id: str
    token: str
    original_meaning: str
    last_used_tick: int
    compression_ratio: float  # How much it was compressed before death
    etymology: list[str]      # Chain of previous meanings

    @property
    def depth(self) -> int:
        """Deeper fossils are older and more potent."""
        return len(self.etymology)

    def excavate(self) -> dict[str, Any]:
        """Extract the original meaning from the fossil."""
        return {
            "word": self.token,
            "meaning": self.original_meaning,
            "etymology_depth": self.depth,
            "lineage": self.etymology,
            "compression": round(self.compression_ratio, 4),
        }


class SemanticStrata:
    """Manages the layered history of word usage across all dialects."""

    FOSSILIZATION_THRESHOLD = 50   # Ticks of disuse before fossilizing

    def __init__(self) -> None:
        self._active_words: dict[str, dict[str, Any]] = {}  # token -> {meaning, last_used, uses}
        self._fossil_layer: list[SemanticFossil] = []
        self._excavation_log: list[dict[str, Any]] = []
        self._tick = 0

    def use_word(self, token: str, meaning: str) -> None:
        """Register word usage; prevents fossilization."""
        self._tick += 1
        if token in self._active_words:
            self._active_words[token]["last_used"] = self._tick
            self._active_words[token]["uses"] += 1
        else:
            self._active_words[token] = {
                "meaning": meaning, "last_used": self._tick, "uses": 1,
            }

    def tick(self) -> list[SemanticFossil]:
        """Check for words that should fossilize due to disuse."""
        newly_fossilized = []
        dead_tokens = []

        for token, info in self._active_words.items():
            ticks_since_use = self._tick - info["last_used"]
            if ticks_since_use >= self.FOSSILIZATION_THRESHOLD:
                fossil = SemanticFossil(
                    fossil_id=hashlib.sha256(token.encode()).hexdigest()[:10],
                    token=token,
                    original_meaning=info["meaning"],
                    last_used_tick=info["last_used"],
                    compression_ratio=info["uses"] / max(ticks_since_use, 1),
                    etymology=[info["meaning"]],
                )
                self._fossil_layer.append(fossil)
                newly_fossilized.append(fossil)
                dead_tokens.append(token)

        for token in dead_tokens:
            del self._active_words[token]

        return newly_fossilized

    def excavate(self, depth: int = 1) -> list[dict[str, Any]]:
        """Dig into the fossil layer. Returns the N deepest fossils."""
        sorted_fossils = sorted(self._fossil_layer, key=lambda f: -f.depth)
        results = [f.excavate() for f in sorted_fossils[:depth]]
        self._excavation_log.extend(results)
        return results

    def revive_word(self, token: str) -> bool:
        """Attempt to bring a fossilized word back into active use."""
        fossil = next((f for f in self._fossil_layer if f.token == token), None)
        if not fossil:
            return False

        self.use_word(token, f"REVIVED({fossil.original_meaning})")
        self._fossil_layer.remove(fossil)
        return True

    @property
    def stats(self) -> dict[str, Any]:
        active_count = len(self._active_words)
        fossil_count = len(self._fossil_layer)
        avg_depth = (
            sum(f.depth for f in self._fossil_layer) / max(fossil_count, 1)
        )
        oldest_fossil = max(
            (f.last_used_tick for f in self._fossil_layer), default=0
        )
        return {
            "active_vocabulary": active_count,
            "fossilized_words": fossil_count,
            "avg_fossil_depth": round(avg_depth, 2),
            "oldest_fossil_tick": oldest_fossil,
            "total_excavations": len(self._excavation_log),
        }
