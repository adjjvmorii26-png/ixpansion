"""Voice — the organism speaks through its own grammar.

No language model. The voice is assembled from the same hex grammar
that grew the body, so the poem and the organism share one skeleton.
"""
from __future__ import annotations

from typing import List

from .seed import VERBS, SYLLABLES, pseudo_word, species_from_hex


def poem(seed: str, cells: int, depth: int) -> List[str]:
    """One verse line per growth layer, from the hex grammar."""
    species = species_from_hex(seed)
    lines: List[str] = []
    total = max(3, min(cells, 9))
    for i in range(total):
        word = pseudo_word(seed, i * 2 + 1)
        word2 = pseudo_word(seed, i * 2 + 3)
        verb = VERBS[int(seed[(i * 2) % max(1, len(seed) - 1)], 16) % len(VERBS)]
        rest = SYLLABLES[int(seed[(i) % max(1, len(seed) - 1)], 16) % len(SYLLABLES)]
        lines.append(f"{word} {word2} {verb} in {rest.lower()} light")
    lines.append(f"— {species}, grown from {seed[:10]}…")
    return lines
