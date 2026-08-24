#!/usr/bin/env python3
"""Inject repeated present to trigger gamma echo collision."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
LAYERS = HERE / "layers.py"
def probe(phrase: str = "lattice holds") -> dict:
    results = []
    for _ in range(3):
        r = subprocess.run([sys.executable, str(LAYERS), phrase], capture_output=True, text=True)
        try:
            results.append(json.loads(r.stdout))
        except Exception:
            results.append({"raw": (r.stdout or "")[-200:]})
    return {"probes": len(results), "last": results[-1] if results else {}}
if __name__ == "__main__":
    print(json.dumps(probe(" ".join(sys.argv[1:]) or "lattice holds"), indent=2))
