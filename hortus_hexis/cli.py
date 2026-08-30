"""HORTUS HEXIS — the garden CLI.

Plant a seed from words; water it; hear it sing; bind it into the
repo. Run from the repo root:

    python -m hortus_hexis.cli "the void blooms between our words"

Commands:
    bare words      grow a new organism from your words and bind it
    status          list the garden ledger
    water <name>    bind an already-grown organism into the repo
    lineage <name>  trace an organism's ancestors by seed
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hortus_hexis.artifacts import safe_name, transcribe  # noqa: E402
from hortus_hexis.autogenesis import grow_and_gate  # noqa: E402
from hortus_hexis.growth import Organism  # noqa: E402
from hortus_hexis.registry import all, lineage, record  # noqa: E402
from hortus_hexis.seed import (  # noqa: E402
    species_from_hex, words_to_seed,
)
from hortus_hexis.voice import poem  # noqa: E402


def _describe(o: Organism) -> None:
    print(f"  species    {o.name}")
    print(f"  seed       {o.seed[:24]}…")
    print(f"  cells      {len(o.cells)}")
    print(f"  vitality   {o.vitality}")
    for line in o.to_art():
        print(line)
    print("  voice:")
    for line in poem(o.seed, len(o.cells), o.box["depth"]):
        print("    " + line)


def cmd_status(args) -> None:
    rows = all()
    if not rows:
        print("  the garden is empty — plant a seed.")
        return
    print(f"  {len(rows)} organism(s) planted:")
    for e in rows:
        mark = "●" if e["checked"] else "○"
        print(f"  {mark} {e['name']:<20} seed {e['seed'][:10]}…  commit {e.get('commit') or '—'}")
    print("  ● = bound into the repo   ○ = grown, ungated")


def cmd_water(args) -> None:
    name = safe_name(args.name)
    spec = Path("hortus_hexis/organisms") / f"{name}.json"
    if not spec.exists():
        print(f"  no organism named {name!r} — try growing one first.")
        return
    data = json.loads(spec.read_text())
    stats = data["stats"]
    result = grow_and_gate(name, data["seed"], data["words"], stats, commit=True, verbose=True)
    if result["gate"] == "open" and result["commit"]:
        record(name, data["seed"], data["song_text"], 1, result["commit"])
        print(f"  watered and planted: {result['commit']}")


def cmd_lineage(args) -> None:
    rows = all()
    match = [e for e in rows if e["name"].startswith(safe_name(args.name))]
    if not match:
        print(f"  no lineage for {args.name!r}")
        return
    for e in match:
        print(f"  {e['name']}  seed={e['seed'][:16]}…  checked={e['checked']}  commit={e.get('commit') or '—'}")
    print(f"  (lineage by seed: {match[0]['seed'][:10]}…)")


def cmd_plant(words: str, commit: bool = True) -> None:
    seed = words_to_seed(words)
    name = species_from_hex(seed)
    o = Organism(name, seed, words)
    print(f"✿ {name} — a new organism stirring from your words.")
    _describe(o)
    print("  binding it into the repo through its newborn gate…")
    result = grow_and_gate(name, seed, words, o.to_dict(), commit=commit, verbose=True)
    if result["gate"] == "open":
        if result["commit"]:
            record(name, seed, o.box and "", 1, result["commit"])
        else:
            record(name, seed, o.box and "", 1, "")
        print(f"  ◈ {name} is now part of HORTUS HEXIS.")


def main(argv=None):
    argv = argv or sys.argv
    if len(argv) > 1 and argv[1] in ("status", "water", "lineage", "help"):
        if argv[1] == "status":
            cmd_status(argparse.Namespace())
        elif argv[1] == "water":
            cmd_water(argparse.Namespace(name=argv[2] if len(argv) > 2 else ""))
        elif argv[1] == "lineage":
            cmd_lineage(argparse.Namespace(name=argv[2] if len(argv) > 2 else ""))
        return
    words = " ".join(argv[1:])
    if not words:
        print("  ~ plant a seed:\n    python -m hortus_hexis.cli \"your words here\"\n    python -m hortus_hexis.cli status | water <name> | lineage <name>")
        return
    cmd_plant(words)


if __name__ == "__main__":
    main()
