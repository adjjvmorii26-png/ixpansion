#!/usr/bin/env python3
"""Branching signal router — maps intent tokens to cortical regions."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

MAP = Path(__file__).resolve().parent / "cortex_map.json"

def route(signal: str) -> dict:
    regions = json.loads(MAP.read_text())["regions"]
    h = int(hashlib.sha256(signal.encode()).hexdigest()[:8], 16)
    r = regions[h % len(regions)]
    strength = (h % 1000) / 1000.0
    return {"signal": signal[:80], "region": r["id"], "role": r["role"], "strength": strength}

if __name__ == "__main__":
    import sys
    print(json.dumps(route(" ".join(sys.argv[1:]) or "pulse"), indent=2))
