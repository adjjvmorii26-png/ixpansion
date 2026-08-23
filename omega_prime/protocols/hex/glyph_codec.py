"""Glyph codec — emergent compression protocol.

Agents communicate using a dynamically-built symbol table. Common
message patterns get progressively shorter glyph encodings. The
codec learns from usage: the more a pattern appears, the more
compressed its encoding becomes.

This is not a fixed protocol — it's a protocol that evolves.
"""
from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any

# Unicode glyph ranges for visual distinction
GLYPHS = "◆◇◈◉○●◐◑◒◓★☆✦✧✩✪✫✬✭✮✯"


@dataclass
class GlyphEntry:
    pattern_hash: str
    original_length: int
    glyph: str
    frequency: int = 1


class GlyphCodec:
    """Adaptive codec that builds its own symbol table from message history."""

    MIN_PATTERN_LEN = 3       # Minimum chars for a compressible pattern
    PROMOTION_THRESHOLD = 3   # Frequency needed to earn a glyph

    def __init__(self) -> None:
        self._table: dict[str, GlyphEntry] = {}  # pattern_hash -> entry
        self._glyph_pool = list(GLYPHS)
        self._assigned: set[str] = set()
        self._usage_counter: Counter[str] = Counter()

    def _pattern_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()[:12]

    def encode(self, payload: dict[str, Any]) -> str:
        """Encode dict to glyph string. Frequent patterns become single glyphs."""
        raw = str(payload)
        compressed_parts: list[str] = []

        # Look for known patterns in the serialized string
        remaining = raw
        while remaining:
            best_match = None
            for phash, entry in sorted(self._table.items(), key=lambda x: -x[1].frequency):
                if entry.glyph in remaining and len(entry.pattern_hash) >= self.MIN_PATTERN_LEN:
                    # We stored the hash, but need to check if we can find the actual substring
                    pass

            # Simple approach: check if any registered pattern matches the start
            matched = False
            for phash, entry in sorted(self._table.items(), key=lambda x: -x[1].frequency):
                if remaining.startswith(entry.pattern_hash[:len(entry.pattern_hash)]):
                    compressed_parts.append(entry.glyph)
                    remaining = remaining[len(entry.pattern_hash):]
                    matched = True
                    break

            if not matched:
                compressed_parts.append(remaining[0])
                remaining = remaining[1:]

            self._usage_counter[raw] += 1

        return "".join(compressed_parts)

    def learn(self, payload: dict[str, Any]) -> str | None:
        """Register a new pattern if it's been seen enough times.
        Returns the assigned glyph or None."""
        raw = str(payload)
        pkey = self._pattern_key(raw)
        freq = self._usage_counter[pkey]

        if freq < self.PROMOTION_THRESHOLD or pkey in self._table:
            return None

        if not self._glyph_pool:
            return None  # Symbol table full

        glyph = self._glyph_pool.pop(0)
        self._assigned.add(glyph)
        entry = GlyphEntry(pattern_hash=pkey, original_length=len(raw), glyph=glyph, frequency=freq)
        self._table[pkey] = entry
        return glyph

    def decode(self, encoded: str) -> str:
        """Decode glyph string back (best-effort; glyphs expand to hashes)."""
        result = []
        for char in encoded:
            entry = next((e for e in self._table.values() if e.glyph == char), None)
            if entry:
                result.append(f"[{entry.pattern_hash}]")
            else:
                result.append(char)
        return "".join(result)

    @property
    def stats(self) -> dict[str, Any]:
        total_original = sum(e.original_length * e.frequency for e in self._table.values())
        total_compressed = sum(e.frequency for e in self._table.values())
        ratio = round(total_compressed / max(total_original, 1), 4) if total_original else 0.0
        return {
            "entries": len(self._table),
            "pool_remaining": len(self._glyph_pool),
            "compression_ratio": ratio,
            "top_patterns": [
                {"hash": e.pattern_hash, "freq": e.frequency, "glyph": e.glyph}
                for e in sorted(self._table.values(), key=lambda x: -x.frequency)[:5]
            ],
        }

    def observe(self, payload: dict[str, Any]) -> None:
        """Call this every time a message is sent to track patterns."""
        pkey = self._pattern_key(str(payload))
        self._usage_counter[pkey] += 1
