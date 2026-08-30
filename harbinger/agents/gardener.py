"""Gardener — the agent that plants growth through HORTUS HEXIS.

Takes an idea and grounds it as a planted organism (if the idea is
garden-flavored: words, seeds, hex), or leaves the path to the
archivist. The gardener is the hinge between thought and repo.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[2]

_GARDEN_HINTS = ("seed", "grow", "garden", "plant", "bloom", "hex", "hybrid", "cross")


def run(words: Optional[str] = None, commit: bool = True) -> Dict[str, Any]:
    if not words:
        return {"agent": "gardener", "planted": False, "note": "nothing to plant"}
    try:
        sys.path.insert(0, str(ROOT))
        import hortus_hexis.autogenesis as ag
        from hortus_hexis.growth import Organism
        from hortus_hexis.seed import species_from_hex, words_to_seed
    except Exception as e:
        return {"agent": "gardener", "planted": False, "error": str(e)[:160]}

    seed = words_to_seed(words)
    name = species_from_hex(seed)
    o = Organism(name, seed, words)
    res = ag.grow_and_gate(name, seed, words, o.to_dict(), commit=commit, verbose=False,
                           parents=[])
    if res["gate"] == "open":
        return {"agent": "gardener", "planted": True, "name": name, "commit": res.get("commit"),
                "vitality": o.vitality}
    return {"agent": "gardener", "planted": False, "name": name, "gate": "closed"}


def is_garden_idea(idea: str) -> bool:
    return any(h in idea.lower() for h in _GARDEN_HINTS)
