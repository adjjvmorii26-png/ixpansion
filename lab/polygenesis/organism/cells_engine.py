#!/usr/bin/env python3
"""List organism cells and soft health."""
from __future__ import annotations
import json
from pathlib import Path
CELLS = Path(__file__).resolve().parent / "cells"
def status() -> dict:
    cells = []
    if CELLS.exists():
        for p in sorted(CELLS.glob("*.org")):
            cells.append({"id": p.stem, "bytes": p.stat().st_size})
    return {"cells": cells, "n": len(cells), "ok": len(cells) >= 4}
if __name__ == "__main__":
    print(json.dumps(status(), indent=2))
