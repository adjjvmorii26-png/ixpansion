#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
SE = Path(__file__).resolve().parent.parent
def run(alt_km=550.0, value=0.52):
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "sat_id": "SAT-LAB", "lat": 0.0, "lon": 0.0, "alt_km": alt_km, "value": value, "ethics_ok": True}
    decision = json.loads(subprocess.run([sys.executable, str(SE / "EMERGENT_LAYER" / "reasoning" / "reason_engine.py")], capture_output=True, text=True).stdout or "{}")
    pk = json.loads(subprocess.run([sys.executable, str(SE / "PK_HEX" / "bind.py")], capture_output=True, text=True).stdout or "{}")
    alt_ok = 150 <= alt_km <= 40000
    return {"ok": alt_ok and decision.get("ok"), "orbital": rec, "alt_ok": alt_ok, "decision": decision, "pk": pk.get("pk")}
if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
