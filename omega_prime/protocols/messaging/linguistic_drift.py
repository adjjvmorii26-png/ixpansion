"""Linguistic drift — emergent language evolution.

Agents communicate using a shared lexicon. Each time a word is used,
its meaning shifts slightly. Isolated groups develop incompatible
vocabularies. When two groups reconnect after separation, they may
discover they've become mutually unintelligible.

This models real linguistic drift: semantic bleaching, semantic
narrowing, and coinage emerge naturally from usage patterns.
"""
from __future__ import annotations

import random
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Word:
    token: str
    meaning: str                    # Current semantic mapping
    original_meaning: str           # What it meant when coined
    usage_count: int = 0            # Times used (drives drift)
    drift_accumulated: float = 0.0  # Total semantic displacement

    @property
    def has_drifted(self) -> bool:
        return self.meaning != self.original_meaning

    def to_dict(self) -> dict[str, Any]:
        return {
            "token": self.token,
            "meaning": self.meaning,
            "original": self.original_meaning,
            "drifted": self.has_drifted,
            "uses": self.usage_count,
        }


class Dialect:
    """A community's shared vocabulary."""

    def __init__(self, dialect_id: str) -> None:
        self.dialect_id = dialect_id
        self._lexicon: dict[str, Word] = {}
        self._usage_log: list[dict[str, str]] = []

    def coin(self, token: str, meaning: str) -> Word:
        if token in self._lexicon:
            return self._lexicon[token]
        word = Word(token=token, meaning=meaning, original_meaning=meaning)
        self._lexicon[token] = word
        return word

    def use(self, token: str) -> dict[str, Any] | None:
        """Use a word; this triggers semantic drift."""
        word = self._lexicon.get(token)
        if not word:
            return None
        word.usage_count += 1
        self._usage_log.append({"token": token, "tick": len(self._usage_log)})
        return {"token": token, "current_meaning": word.meaning}

    def tick_drift(self, rng: random.Random, intensity: float = 0.1) -> list[dict[str, str]]:
        """Apply semantic drift to frequently-used words."""
        drifted_words = []
        for token, word in self._lexicon.items():
            if word.usage_count < 3:
                continue
            if rng.random() > intensity * min(word.usage_count / 10, 1.0):
                continue

            old_meaning = word.meaning
            # Drift toward related meanings
            drift_type = rng.choice(["narrow", "broaden", "shift", "invert"])
            if drift_type == "narrow":
                word.meaning = f"SPECIFIC({old_meaning})"
            elif drift_type == "broaden":
                word.meaning = f"CATEGORY({old_meaning})"
            elif drift_type == "shift":
                word.meaning = f"ADJACENT({old_meaning})"
            elif drift_type == "invert":
                word.meaning = f"OPPOSITE({old_meaning})"

            word.drift_accumulated += 1
            drifted_words.append({
                "token": token,
                "from": old_meaning[:40],
                "to": word.meaning[:40],
                "type": drift_type,
            })
        return drifted_words

    def mutual_intelligibility(self, other: "Dialect") -> float:
        """How well can two dialects understand each other? (0-1)"""
        shared_tokens = set(self._lexicon) & set(other._lexicon)
        if not shared_tokens:
            return 0.0

        matches = sum(
            1 for t in shared_tokens
            if self._lexicon[t].meaning == other._lexicon[t].meaning
        )
        return matches / len(shared_tokens)

    def merge(self, other: "Dialect") -> int:
        """Borrow unknown words from another dialect. Returns count borrowed."""
        borrowed = 0
        for token, word in other._lexicon.items():
            if token not in self._lexicon:
                self.coin(token, f"BORROWED({word.meaning})")
                borrowed += 1
        return borrowed

    @property
    def size(self) -> int:
        return len(self._lexicon)

    @property
    def vocabulary(self) -> list[dict[str, Any]]:
        return [w.to_dict() for w in sorted(self._lexicon.values(), key=lambda x: -x.usage_count)]


class LanguageEvolution:
    DRIFT_INTENSITY = 0.08
    COINAGE_CHANCE = 0.05

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._dialects: dict[str, Dialect] = {}
        self._tick = 0
        self._drift_events: list[dict[str, Any]] = []
        self._coinage_count = 0

    def create_dialect(self, dialect_id: str) -> Dialect:
        d = Dialect(dialect_id=dialect_id)
        self._dialects[dialect_id] = d
        return d

    def seed_vocabulary(self, dialect_id: str, vocab: dict[str, str]) -> None:
        d = self._dialects.get(dialect_id)
        if not d:
            d = self.create_dialect(dialect_id)
        for token, meaning in vocab.items():
            d.coin(token, meaning)

    def simulate_usage(self, dialect_id: str, tokens_used: list[str]) -> list[dict[str, Any]]:
        d = self._dialects.get(dialect_id)
        if not d:
            return []
        results = []
        for token in tokens_used:
            result = d.use(token)
            if result:
                results.append(result)

            # Random coinage of new words
            if self._rng.random() < self.COINAGE_CHANCE:
                new_token = f"w{hashlib.md5(f'{self._rng.random()}'.encode()).hexdigest()[:6]}"
                new_meaning = f"CONCEPT_{self._coinage_count}"
                d.coin(new_token, new_meaning)
                self._coinage_count += 1
                results.append({"coined": new_token, "meaning": new_meaning})

        return results

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        all_drifts = []
        for did, dialect in self._dialects.items():
            drifts = dialect.tick_drift(self._rng, intensity=self.DRIFT_INTENSITY)
            for d in drifts:
                d["dialect"] = did
            all_drifts.extend(drifts)

        self._drift_events.extend(all_drifts)
        intelligibility_matrix = self._compute_intelligibility()

        return {
            "tick": self._tick,
            "drift_events": len(all_drifts),
            "total_coined": self._coinage_count,
            "intelligibility": intelligibility_matrix,
        }

    def _compute_intelligibility(self) -> dict[str, dict[str, float]]:
        ids = list(self._dialects.keys())
        matrix = {}
        for a in ids:
            matrix[a] = {}
            for b in ids:
                if a != b and a in self._dialects and b in self._dialects:
                    matrix[a][b] = round(self._dialects[a].mutual_intelligibility(self._dialects[b]), 4)
        return matrix

    @property
    def drift_timeline(self) -> list[dict[str, Any]]:
        return self._drift_events[-20:]
