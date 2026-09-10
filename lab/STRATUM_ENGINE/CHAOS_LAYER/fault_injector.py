#!/usr/bin/env python3
from __future__ import annotations
import json, random, sys
FAULTS = ["drop_sample", "spike_value", "negate_ethics", "delay_sim", "duplicate"]
def inject(record, fault=None, seed=0):
    rng = random.Random(seed)
    fault = fault or rng.choice(FAULTS)
    out = dict(record)
    if fault == "drop_sample":
        return {"ok": True, "fault": fault, "dropped": True, "record": None}
    if fault == "spike_value": out["value"] = float(out.get("value", 0)) * 50
    elif fault == "negate_ethics": out["ethics_ok"] = False
    elif fault == "duplicate": out["dup"] = True
    elif fault == "delay_sim": out["delay_ms"] = 250
    return {"ok": True, "fault": fault, "record": out}
if __name__ == "__main__":
    print(json.dumps(inject({"value": 1.0, "ethics_ok": True, "source": "chaos"}, sys.argv[1] if len(sys.argv)>1 else None, 42), indent=2))
