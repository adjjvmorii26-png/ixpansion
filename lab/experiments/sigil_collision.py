#!/usr/bin/env python3
"""Detect near-collisions in sigil hue space (orthogonality hygiene)."""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path

AGENTS = ["forge_mind", "wanderer", "archivist", "sentinel", "mimic", "pulse_driver", "void", "flux"]
OUT = Path(__file__).resolve().parent / "sigil_collisions.json"
THRESHOLD = 0.35

def vec(name: str) -> tuple[float, float]:
    h = hashlib.sha256(name.encode()).hexdigest()
    a = int(h[:8], 16) / 0xFFFFFFFF * 2 * math.pi
    return math.cos(a), math.sin(a)

def main() -> dict:
    nodes = {n: vec(n) for n in AGENTS}
    hits = []
    names = list(nodes)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = nodes[names[i]], nodes[names[j]]
            cos = a[0] * b[0] + a[1] * b[1]
            if cos > THRESHOLD:
                hits.append({"a": names[i], "b": names[j], "cos": round(cos, 4)})
    out = {"threshold": THRESHOLD, "collisions": hits, "ok": len(hits) == 0}
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return out

if __name__ == "__main__":
    main()
