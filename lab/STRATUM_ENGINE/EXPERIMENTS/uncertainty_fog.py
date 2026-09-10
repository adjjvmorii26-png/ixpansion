#!/usr/bin/env python3
"""Uncertainty Fog — ELRP band as 2D fog density field."""
from __future__ import annotations
import json, math, sys
def fog(fused=0.49, uncertainty=0.1, threshold=0.5, n=9):
    cells = []
    for i in range(n):
        x = -1.0 + 2.0 * i / (n - 1)
        d = 1.0 - math.exp(-((x - fused) ** 2) / (2 * max(uncertainty, 1e-6) ** 2))
        zone = "clearing" if d < 0.35 else ("mist" if d < 0.7 else "fog")
        cells.append({"x": round(x, 3), "density": round(d, 4), "zone": zone})
    low, high = fused - uncertainty, fused + uncertainty
    if high < threshold: action = "hold"
    elif low > threshold: action = "act"
    else: action = "observe"
    return {"ok": True, "experiment": "uncertainty_fog", "fused": fused, "uncertainty": uncertainty, "threshold": threshold, "action": action, "field": cells}
if __name__ == "__main__":
    f = float(sys.argv[1]) if len(sys.argv) > 1 else 0.49
    u = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
    print(json.dumps(fog(f, u), indent=2))
