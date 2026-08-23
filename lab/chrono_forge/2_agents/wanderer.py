#!/usr/bin/env python3
"""Wanderer — proposes unique experiment module names from hash (no unsafe writes)."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone

STEMS = ["echo", "flux", "glyph", "orbit", "prism", "quill", "rift", "spark", "tide", "vault"]
MODES = ["bind", "fold", "mesh", "scan", "seal", "tune", "weave", "yield"]

def propose(n: int = 5) -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    h = hashlib.sha256(ts.encode()).hexdigest()
    ideas = []
    for i in range(n):
        chunk = h[i * 4 : i * 4 + 8]
        stem = STEMS[int(chunk[:2], 16) % len(STEMS)]
        mode = MODES[int(chunk[2:4], 16) % len(MODES)]
        name = f"{stem}_{mode}_{chunk[4:].lower()}"
        ideas.append({"module": f"lab/experiments/{name}.py", "sigil": f"0x{chunk.upper()}"})
    return {"agent": "wanderer", "ts": ts, "proposals": ideas}

if __name__ == "__main__":
    print(json.dumps(propose(), indent=2))
