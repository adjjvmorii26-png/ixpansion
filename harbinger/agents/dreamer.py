"""Dreamer — the agent that imagines what the frontier could become.

The Dreamer does not read code for what it is; it reads module names
for what they imply. By fusing the vocabulary of *disconnected* modules
it synthesizes new, never-written concepts — a "dream" of a module the
frontier has not yet grown. Overseer can then choose to plant it.

Dreaming is deterministic and offline: same frontier, same dreamscape,
same children.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
API_DIR = ROOT / "api"

_WORD = re.compile(r"[a-z]+")


def module_names() -> List[str]:
    """The seeds of the dream: every module's snake_case name."""
    if not API_DIR.exists():
        return []
    names = []
    for p in sorted(API_DIR.glob("*.py")):
        stem = p.stem
        if stem in ("__init__", "index", "unified_router"):
            continue
        names.append(stem)
    return names


def _tokens(name: str) -> List[str]:
    return _WORD.findall(name)


def _pair_affinity(a: str, b: str, salt: str = "") -> int:
    """A stable, content-based affinity between two module names."""
    h = hashlib.sha256(f"{a}::{b}::{salt}".encode()).hexdigest()
    return int(h[:4], 16)


def dream(salt: str = "the frontier dreams onward", k: int = 6, tense: float = 0.0,
         focus: str = "") -> Dict[str, Any]:
    """Synthesize k new module concepts from existing module vocabulary.

    Each dream fuses two *affinity-matched* words from different modules
    to produce a never-written species name. `tense` raises how novel
    (vs. conservative) fusions are. `focus` anchors every dream on a
    single word the caller wants to echo (e.g. a user query).
    """
    names = module_names()
    if len(names) < 2:
        return {"agent": "dreamer", "dreams": [], "note": "frontier too young to dream"}

    # Build a word pool from module roots (take first token, which is the
    # most species-defining part of each snake_case name).
    pool: List[str] = []
    for n in names:
        toks = _tokens(n)
        if toks:
            pool.append(toks[0])
    pool = sorted(set(pool))

    dreams: List[Dict[str, Any]] = []
    seen: set = set()
    attempts = 0
    while len(dreams) < k and attempts < k * 40:
        attempts += 1
        # pick two distinct root words by stable affinity
        ranked = sorted(pool, key=lambda w: _pair_affinity(w, salt, str(attempts)))
        # slide by `tense` to favor more-distant pairings
        idx = min(len(pool) - 1, int(tense * len(pool) / 2))
        if focus and focus != "":  # anchor on the echoed word
            w1 = focus if focus in pool else focus
            w2 = ranked[(idx + 1 + int(tense * 3)) % len(pool)] if len(pool) > 1 else None
        else:
            w1 = ranked[idx % len(pool)] if pool else None
            w2 = ranked[(idx + 1 + int(tense * 3)) % len(pool)] if len(pool) > 1 else None
        if not w1 or not w2 or w1 == w2:
            continue
        dream_name = f"{w1}_{w2}"
        if dream_name in seen:
            continue
        seen.add(dream_name)
        # a short "why this dream matters" grounded in both source words
        rationale = (f"fuses the '{w1}-family' with the '{w2}-family' — "
                     f"a domain the frontier has not yet bridged.")
        dreams.append({"name": dream_name, "fuel": sorted({w1, w2}),
                       "rationale": rationale, "tense": tense})

    return {"agent": "dreamer", "module_pool": len(names), "word_pool": len(pool),
            "dreams": dreams}


def run(salt: str = "the frontier dreams onward", k: int = 6, tense: float = 0.0, focus: str = "") -> Dict[str, Any]:
    return dream(salt=salt, k=k, tense=tense, focus=focus)
