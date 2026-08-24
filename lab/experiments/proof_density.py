#!/usr/bin/env python3
"""Score proof ledger density — growth metric, not vanity views."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "lab" / "unique_path" / "proof_ledger.jsonl"
OUT = Path(__file__).resolve().parent / "proof_density.json"

def measure() -> dict:
    if not LEDGER.exists():
        return {"ok": False, "lines": 0, "density": 0.0}
    lines = [ln for ln in LEDGER.read_text().strip().splitlines() if ln.strip()]
    types = Counter()
    for ln in lines:
        try:
            types[json.loads(ln).get("type", "unknown")] += 1
        except Exception:
            types["corrupt"] += 1
    n = max(len(lines), 1)
    density = round(len(types) / (n ** 0.5), 4)
    out = {"ok": True, "lines": n, "unique_types": len(types),
           "types": dict(types.most_common(12)), "density": density}
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    return out

if __name__ == "__main__":
    print(json.dumps(measure(), indent=2))
