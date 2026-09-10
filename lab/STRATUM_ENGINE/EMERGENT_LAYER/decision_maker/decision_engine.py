#!/usr/bin/env python3
from __future__ import annotations
import json
def decide(fused=0.48, uncertainty=0.1, threshold=0.5):
    low, high = fused - uncertainty, fused + uncertainty
    if high < threshold: action = "hold"
    elif low > threshold: action = "act"
    else: action = "observe"
    return {"ok": True, "fused": fused, "band": [round(low, 4), round(high, 4)], "threshold": threshold, "action": action}
if __name__ == "__main__":
    print(json.dumps(decide(), indent=2))
