"""Cross-pollination — two seeds fuse into a hybrid organism.

The hybrid inherits from both parents: its seed is a byte-level
interleave-XOR fusion salted with the parents' joint digest, and its
species name is a genetic splice of both parent names. Crucially the
fusion is deterministic: the same two parents always grow the same
hybrid — cross just once, keep the child forever.
"""
from __future__ import annotations

import hashlib
from typing import List

from .seed import words_to_seed


def hybrid_seed(seed_a: str, seed_b: str) -> str:
    """Fuse two hex seeds into a deterministic hybrid hex seed."""
    ra = bytes.fromhex(seed_a)
    rb = bytes.fromhex(seed_b)
    n = max(len(ra), len(rb))
    fused = bytearray()
    for i in range(n):
        ca = ra[i] if i < len(ra) else 0x00
        cb = rb[i] if i < len(rb) else 0x00
        fused.append((ca ^ cb) ^ ((i * 7) & 0xFF))
    fused.extend(hashlib.sha256((seed_a + ":" + seed_b).encode()).digest()[:8])
    return fused.hex()


def hybrid_name(name_a: str, name_b: str) -> str:
    """Genetic splice: leading half of A + trailing half of B."""
    a = max(1, len(name_a) // 2 + 1)
    b = len(name_b) // 2
    spliced = name_a[:a] + name_b[b:]
    return spliced or "hybrid"


def hybrid_pair(name_a: str, name_b: str, seeds: List[str]) -> str:
    """Let the garden re-derive its own ancestry from registry seeds."""
    return hybrid_seed(seeds[0], seeds[1])


def words_hybrid(words_a: str, words_b: str):
    """Convenience: two utterances -> (hybrid_seed, hybrid_name)."""
    sa = words_to_seed(words_a)
    sb = words_to_seed(words_b)
    return hybrid_seed(sa, sb)
