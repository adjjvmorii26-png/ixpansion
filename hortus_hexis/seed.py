"""Seed forge — turns spoken words into a hex genome.

The chain: words -> utf-8 bytes -> hex seed -> genome.
Every byte of the seed drives a growth rule, a heat phase, and a
lethargy hold, so no two utterances ever grow the same organism.
"""
from __future__ import annotations

import hashlib
from typing import Dict, List

# Cosmic syllables indexed by hex nibble (voice material).
SYLLABLES = "veln lumex amar xeth orev nys sil drak uri qo vedh miron syphex kal orak yndr"
SYLLABLES = SYLLABLES.split()

# Suffixes by branch rule (0-7) for pseudo-words.
SUFFIXES = ["ia", "eth", "or", "us", "is", "yx", "on", "ar"]

# Verbs for the voice lines, indexed by branch rule.
VERBS = ["blooms", "curls", "loops", "spirals", "cracks", "weaves", "drifts", "haunts"]


def words_to_seed(text: str) -> str:
    """Conversation -> hex seed string."""
    return text.encode("utf-8").hex()


def seed_digest(seed: str) -> str:
    return hashlib.sha256(seed.encode()).hexdigest()


def genome_from_hex(seed: str) -> Dict[str, List[float]]:
    """Hex seed -> genome of branch rules, heat phases, lethargy holds."""
    try:
        raw = bytes.fromhex(seed)
    except ValueError:
        raw = b"\x07"
    if not raw:
        raw = b"\x07"
    genome: Dict[str, List[float]] = {"rules": [], "heat": [], "lethargy": []}
    for byte in raw:
        genome["rules"].append(float(byte % 8))
        genome["heat"].append((byte / 255.0) * 6.283185307179586)
        genome["lethargy"].append(float((byte * 7) % 13))
    return genome


def species_from_hex(seed: str) -> str:
    """First 6 hex chars -> 3 syllables -> species name."""
    clean = "".join(ch for ch in seed if ch in "0123456789abcdef")
    padded = (clean + "000000")[:6]
    parts = []
    for i in range(0, 6, 2):
        idx = int(padded[i:i + 2], 16) % len(SYLLABLES)
        parts.append(SYLLABLES[idx])
    return "".join(parts)


def hex_tail(seed: str) -> str:
    return (seed + "00")[:6] if seed else "00"


def pseudo_word(seed: str, i: int) -> str:
    """Derive a deterministic pseudo-word from the seed's nibbles."""
    clean = (seed + "0" * 16)[::-1]  # reversed so early words differ from species
    part = clean[(i * 2) % max(1, len(clean) - 1): (i * 2) % max(1, len(clean) - 1) + 2]
    if not part or len(part) < 2:
        part = "0f"
    a = SYLLABLES[int(part[0], 16) % len(SYLLABLES)]
    b = SUFFIXES[int(part[1], 16) % len(SUFFIXES)]
    return (a + b).lower()
