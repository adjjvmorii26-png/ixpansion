#!/usr/bin/env python3
"""Load genome traits + constraints."""
from __future__ import annotations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
def load() -> dict:
    traits = []
    tbl = HERE / "genome_traits.tbl"
    if tbl.exists():
        lines = tbl.read_text().strip().splitlines()[1:]
        for ln in lines:
            parts = ln.split("\t")
            if len(parts) >= 2:
                traits.append({"trait": parts[0], "weight": float(parts[1])})
    mut = json.loads((HERE / "genome_mutations.map").read_text()) if (HERE / "genome_mutations.map").exists() else {}
    root = (HERE / "genome_root.hex").read_text().strip() if (HERE / "genome_root.hex").exists() else None
    return {"traits": traits, "mutations": mut, "root": root}
if __name__ == "__main__":
    print(json.dumps(load(), indent=2))
