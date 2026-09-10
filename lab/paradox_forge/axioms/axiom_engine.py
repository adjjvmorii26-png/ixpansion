#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
def load() -> dict:
    root = (HERE / "axiom_root.ax").read_text().strip().splitlines()[0] if (HERE / "axiom_root.ax").exists() else None
    frags = []
    tbl = HERE / "axiom_fragments.tbl"
    if tbl.exists():
        for ln in tbl.read_text().strip().splitlines()[1:]:
            parts = ln.split("\t")
            if len(parts) >= 2:
                frags.append({"id": parts[0], "claim": parts[1]})
    return {"root": root, "fragments": frags}
if __name__ == "__main__":
    print(json.dumps(load(), indent=2))
