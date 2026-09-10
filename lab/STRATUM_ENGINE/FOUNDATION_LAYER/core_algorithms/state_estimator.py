#!/usr/bin/env python3
from __future__ import annotations
import json, sys
def estimate(values, alpha=0.3):
    if not values: return {"ok": False, "err": "empty"}
    s = float(values[0])
    for v in values[1:]: s = alpha * float(v) + (1 - alpha) * s
    return {"ok": True, "estimate": round(s, 6), "n": len(values), "alpha": alpha}
if __name__ == "__main__":
    vals = [float(x) for x in sys.argv[1:]] or [1.0, 1.2, 0.9, 1.1]
    print(json.dumps(estimate(vals), indent=2))
