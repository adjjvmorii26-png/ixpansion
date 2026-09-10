#!/usr/bin/env python3
from __future__ import annotations
import json, sys
def reason(opinions, ethics_ok=True, threshold=0.5, uncertainty=0.1):
    if not ethics_ok:
        return {"ok": True, "protocol": "ELRP-1", "action": "hold", "reason": "ethics_gate", "fused": None, "band": None}
    if not opinions:
        return {"ok": False, "err": "no_opinions", "protocol": "ELRP-1"}
    num = sum(o.get("value", 0) * o.get("weight", 1) * o.get("confidence", 1) for o in opinions)
    den = sum(o.get("weight", 1) * o.get("confidence", 1) for o in opinions) or 1
    fused = num / den
    low, high = fused - uncertainty, fused + uncertainty
    if high < threshold: action, why = "hold", "below_threshold"
    elif low > threshold: action, why = "act", "above_threshold"
    else: action, why = "observe", "band_crosses_threshold"
    return {"ok": True, "protocol": "ELRP-1", "fused": round(fused, 6), "band": [round(low, 4), round(high, 4)], "threshold": threshold, "action": action, "reason": why, "n_opinions": len(opinions)}
if __name__ == "__main__":
    demo = [{"source": "estimator", "value": 0.45, "weight": 1.0, "confidence": 1.0}, {"source": "scout", "value": 0.55, "weight": 0.8, "confidence": 0.9}]
    print(json.dumps(reason(demo, ethics_ok=not (len(sys.argv) > 1 and sys.argv[1] == "fail")), indent=2))
