"""HORTUS HEXIS — the garden in a shell.

An interactive repl where each line you type grows a new organism.
Type a number to rebind (grow again + commit), or:

    status  — list planted organisms
    lineage — show all lineages
    quit    — tend no more tonight

Run:  python -m hortus_hexis
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hortus_hexis.autogenesis import grow_and_gate  # noqa: E402
from hortus_hexis.growth import Organism  # noqa: E402
from hortus_hexis.registry import all, record  # noqa: E402
from hortus_hexis.seed import species_from_hex, words_to_seed  # noqa: E402


def _grow(words: str, commit: bool = True):
    seed = words_to_seed(words)
    name = species_from_hex(seed)
    o = Organism(name, seed, words)
    print(f"✿ from ‘{words[:48]}’ grew **{name}** (vitality {o.vitality}, {len(o.cells)} cells)")
    result = grow_and_gate(name, seed, words, o.to_dict(), commit=commit, verbose=True)
    if result["gate"] == "open":
        record(name, seed, o.box and "", 1, result["commit"] or "")
    return name


def run():
    print("  HORTUS HEXIS — speak, and the garden grows.")
    print("  type words to plant · status · lineage · quit\n")
    while True:
        try:
            line = input("  garden> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  the garden sleeps. until we speak again.")
            return
        if not line:
            continue
        low = line.lower()
        if low in ("quit", "exit", "q"):
            print("  the garden sleeps. until we speak again.")
            return
        if low == "status":
            for e in all():
                print(f"  ● {e['name']:<16} seed {e['seed'][:10]}…")
            continue
        if low == "lineage":
            seen = {}
            for e in all():
                seen.setdefault(e["seed"][:10], []).append(e["name"])
            for seed_pre, names in seen.items():
                print(f"  {seed_pre}… -> " + ", ".join(names))
            continue
        _grow(line)


if __name__ == "__main__":
    run()
