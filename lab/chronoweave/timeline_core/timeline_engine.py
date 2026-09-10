#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
def status() -> dict:
    root = (HERE / "timeline_root.tln").read_text().strip().splitlines()[0] if (HERE / "timeline_root.tln").exists() else None
    branches = json.loads((HERE / "timeline_branches.map").read_text()) if (HERE / "timeline_branches.map").exists() else {}
    return {"root": root, "branches": list(branches.keys()), "n_branches": len(branches)}
if __name__ == "__main__":
    print(json.dumps(status(), indent=2))
